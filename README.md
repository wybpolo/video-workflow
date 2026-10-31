# video-workflow

bingkis 的 AI 视频制作工作流：调研选型后的去重技能栈 + 总控路由技能 + 管线脚本。
给一个文本主题、图片或视频素材，按路线产出成片 MP4（可选剪映可编辑草稿）。

当前版本见 `VERSION`，变更记录见 `CHANGELOG.md`，上游锁定版本见 `UPSTREAM.md`。

## 路线一览（详见 skills/video-workflow/SKILL.md）

| 路线 | 内容 | 引擎 |
|---|---|---|
| A 艺术解说 | 艺术风格动画、Kurzgesagt/Vox/白板/3b1b 风解说片 | huashu-art-motion（上游，install.sh 按锁定 commit 拉取） |
| B 通用设计 | 产品片、数据片、标题卡、竖屏信息片 | HyperFrames（技能已 vendored 在 skills/，二进制资源由 install.sh 补齐） |
| C 图解素材 | 技术概念等距图解 | anatomy（上游，install.sh 拉取） |
| D 全自动短视频 | 主题→脚本→素材→配音→字幕量产 | MoneyPrinterTurbo（上游，install.sh 拉取；需自备 LLM key + Pexels key） |
| E 生成片段 | 文/图生视频实拍感片段 | Muse 原生视频生成；外部备选 Runway Dev API |
| F 素材再加工 | 剪辑、转写、字幕、配音 | ffmpeg + studio/scripts |
| G 剪映草稿 | 成片转可编辑草稿精修 | pyJianYingDraft（studio/scripts/make_jianying_draft.py） |

原则：一支片只用一个渲染引擎（huashu 与 HyperFrames 不同时用）；含图表先过 dataviz。

## 目录

- `skills/video-workflow/` — 总控技能（本仓核心资产）
- `skills/dataviz/` — 图表规范技能（vendored，源 baoyu-design）
- `skills/hyperframes*`、`skills/media-use/` — HyperFrames 官方技能（vendored 文本部分；字体/音效等二进制文件未入库，见 UPSTREAM.md，install.sh 从上游锁定 commit 补齐）
- `studio/scripts/` — assemble.py（拼接/混音/烧字幕）、transcribe.py（faster-whisper 转写）、make_jianying_draft.py（剪映草稿）
- `studio/README-视频工作流.md` — 选型理由、没装什么及原因、验证记录
- `examples/demo/` — 已验证演示成片的字幕与说明
- `install.sh` — 一键恢复全部环境（技能、venv、Playwright Chromium、MoneyPrinterTurbo）

## 恢复 / 安装

在新的 Muse 环境里：

```bash
git clone <this-repo> && cd video-workflow
bash install.sh            # 默认装到 ~/workspace（可用 WORKSPACE=... 覆盖）
```

然后把 `skills/` 下各技能目录复制/链接到 `~/workspace/custom-skills/`（install.sh 已处理）。

## 版本管理

- 每次优化流程：改文件 → 更新 `VERSION`（语义化版本）+ `CHANGELOG.md` → 推送一个新 commit，commit message 以版本号开头，如 `v1.1.0: ...`。
- 上游升级：改 `UPSTREAM.md` 的锁定 commit 并重跑 install.sh 验证后，再升本仓版本。

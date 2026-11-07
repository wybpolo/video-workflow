# video-workflow

bingkis 的 AI 视频制作工作流：调研选型后的去重技能栈 + 总控路由技能 + 管线脚本。
给一个文本主题、图片或视频素材，按路线产出成片 MP4（可选剪映可编辑草稿）。

当前版本见 `VERSION`，变更记录见 `CHANGELOG.md`，上游锁定版本见 `UPSTREAM.md`。

## 路线一览（详见 skills/video-workflow/SKILL.md）

| 路线 | 内容 | 引擎 |
|---|---|---|
| A 艺术解说 | 艺术风格动画、Kurzgesagt/Vox/白板/3b1b 风解说片；子路线：无旁白知识长片 | huashu-art-motion（上游，install.sh 按锁定 commit 拉取）；子路线 vibe-knowledge-film（vendored） |
| B 通用设计 | 产品片、数据片、标题卡、竖屏信息片 | HyperFrames（技能已 vendored 在 skills/，二进制资源由 install.sh 补齐）；高质量选项 Multiplane（运动模糊/景深/确定性自检，引擎由 install.sh 装到 video-studio/apps，按片二选一） |
| C 图解素材 | 技术概念等距图解；真数学/3D 动画；像素特效素材 | anatomy（上游，install.sh 拉取）；manimgx（技能 vendored，引擎 uv 装）；pixelfx（vendored） |
| D 全自动短视频 | 主题→脚本→素材→配音→字幕量产 | MoneyPrinterTurbo（上游，install.sh 拉取；需自备 LLM key + Pexels key） |
| E 生成片段 | 文/图生视频实拍感片段 | Muse 原生视频生成（muse.ai 内免 key，见下节）；外部环境备选 Runway Dev API |
| F 素材再加工 | 剪辑、转写、字幕、配音 | ffmpeg-skill 契约脚本（vendored）+ studio/scripts |
| G 剪映草稿 | 成片转可编辑草稿精修 | pyJianYingDraft（studio/scripts/make_jianying_draft.py） |
| H 短剧生产 | 小说→大纲→角色→美术→剧本→分镜→成片 | shuohao-skills 7 技能（vendored）+ 原生生成出片 |
| I 参考复刻 | 拆解参考片结构 → 换变量量产变体 | rea-video 机读拆解前置（技能 vendored，引擎由 install.sh 装进 studio .venv，须连 rapidocr-onnxruntime）+ 结构卡 + E 路线生成 |

原则：一支片只用一个渲染引擎（huashu 与 HyperFrames 不同时用）；含图表先过 dataviz。

## 生成后端与环境差异（重要，别搞混）

本工作流的**生成能力**（E/H/I 路线的视频生成，以及各路线都会用到的图片生成）依运行环境而定：

- **在 muse.ai（Muse 环境）内**：视频生成与图片生成是内置原生能力，**免 key 直接可用**。视频约 10 秒/条、单次最多 6 条、自带声音、不收音频输入（音乐只能用文字描述氛围）、可按提示词让角色说指定台词（短剧原生对白就靠这个）。**图片生成要善用**：角色锚图、分镜参考图、概念图、贴图等素材缺口优先用它补位，再进合成或视频生成。
- **在外部环境**（本地 Claude Code、其他 agent 运行时、自建服务）：**没有内置生成**，视频与图片生成都必须自备服务商的**接口地址 + key**（如 Runway Dev 聚合 Veo/Kling/Seedance、即梦/Seedance、MiniMax 云端平台等），占位清单见 `skills/video-workflow/SKILL.md` 的「待配置」。未配置时 E/H/I 路线不可直接出片，只能先产出分镜与提示词；不要把「原生生成可用」当成跨环境的前提。
- D 路线（MoneyPrinterTurbo）在任何环境都需要自备 LLM key + Pexels key，与上条无关。

## 目录

- `skills/video-workflow/` — 总控技能（本仓核心资产）
- `skills/dataviz/` — 图表规范技能（vendored，源 baoyu-design）
- `skills/hyperframes*`、`skills/media-use/` — HyperFrames 官方技能（vendored 文本部分；字体/音效等二进制文件未入库，见 UPSTREAM.md，install.sh 从上游锁定 commit 补齐）
- `studio/scripts/` — assemble.py（拼接/混音/烧字幕）、transcribe.py（faster-whisper 转写）、make_jianying_draft.py（剪映草稿）
- `studio/README-视频工作流.md` — 选型理由、没装什么及原因、验证记录
- `examples/demo/` — 实战经验沉淀：四篇案例（PPT 转视频、短剧 v1→v2 教训、参考复刻、v1.3.0 新技能实测）+ v1.0.0 演示基线，做新片前先翻这里避坑
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

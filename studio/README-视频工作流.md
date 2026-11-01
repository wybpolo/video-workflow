# 视频工作流（2026-10-31 搭建）

一句话用法：**你给主题（一段文字）、图片或视频素材，kis 按下面路线做成片。**
总控技能：`video-workflow`（在 custom-skills 里），每次做片先选路线、再走管线。

## 选型结论（调研后去重，每层只留一个）

| 层 | 选用 | 说明 |
|---|---|---|
| 艺术/解说动画引擎 | **huashu-art-motion**（花叔，5.8k★） | 53 张风格配方卡、9 种解说语法、参数化片段、代码配乐、qa+反PPT交付门禁。中文解说/艺术片主力。已装，已实测渲出 1080p 片段 |
| 通用设计视频引擎 | **HyperFrames**（HeyGen，76k★，Apache-2.0） | HTML→MP4 确定性渲染，注册表 ~450 组件。与 huashu 同为「代码→Chrome→ffmpeg」，所以**同一支片只用一个引擎**：设计/数据/产品片用它，艺术解说片用 huashu。已装 4 个技能（核心/CLI/注册表/媒体），CLI v0.8.223 实测可用 |
| 技术图解素材 | **anatomy**（23k★） | 把技术概念做成精密等距 SVG/WebGL 机器图。不是视频工具，是给 A/B 路线供画面的素材层。已装 |
| 图表规范 | **dataviz**（取自 baoyu-design） | 画图表前先过它，配色可验证 |
| 全自动口播短视频 | **MoneyPrinterTurbo**（137k★） | 主题→脚本→素材→配音→字幕→成片量产线。已装到 apps/，CLI 实测可跑；**差两个 key 才能真用**：LLM key + Pexels key（免费申请） |
| 剪映精修 | **pyJianYingDraft** 0.3.1 | 生成剪映可编辑草稿（非成片），你拷到 Windows 剪映草稿目录继续改。已装，已实测生成合法草稿（含真实视频轨+文字轨）。注意：只支持国内剪映，国际 CapCut 不行；自动导出仅剪映 ≤6.x |
| 配音 | Muse 原生 TTS（首选，本机可用） / edge-tts（免费微软音） | edge-tts 在本云 VM 被出口代理掐断（已实测），在你 Windows 本机可正常用；MoneyPrinterTurbo 默认也用它 |
| 字幕/转写 | faster-whisper + SRT/ASS 烧录 | 已装进 .venv；模型首次下载较慢（本 VM 网络），自备口播稿时直接按稿对齐出字幕，不依赖转写 |
| 生成式实拍片段 | Muse 原生视频生成（约10秒/条、自带声音、单次≤6条） | 外部备选 Runway Dev API（一个 key 聚合 Veo/Kling/Seedance，需付费 key）。**Sora API 已下线（2026-09-24），别再考虑** |

## 生成后端与环境差异（重要，别搞混）

- **在 muse.ai（当前 Muse 环境）内**：视频生成与图片生成都是内置原生能力，**免 key 直接可用**。视频约 10 秒/条、单次最多 6 条、自带声音、可按提示词让角色说指定台词；图片生成要善用——角色锚图、分镜参考图、概念图、贴图等素材缺口优先用它补位，再进合成或视频生成。
- **在外部环境**（本地 Claude Code、其他 agent 运行时）：**没有内置生成**，视频/图片生成都必须自备服务商的接口地址 + key 才能用（如 Runway Dev 聚合 Veo/Kling/Seedance、即梦/Seedance、MiniMax 云端等，见总控技能「待配置」）。没配 key 时 E/H/I 路线只能先做到分镜与提示词，不要假装已在生成。
- TTS 是另一回事：原生 TTS 在本环境可用；edge-tts 在本云 VM 被代理掐断、Windows 本机可用（见选型表）。

## 目录约定（2026-11-01 起）

- `projects/` — 正式项目的工程目录（可由脚本再生成，如 byd-t5-tutorial）
- `output/` — 新成片的临时交付落点，交付后按性质归档到下面两处
- `tests/<YYYY-MM-DD>/` — **所有测试片/示例片/验证片**（含其工程），按日期分子目录；**每周一凌晨自动清理超过 14 天的日期目录**（scripts/cleanup_tests.sh + 定时任务），不长期占盘
- `archive/` — **需长期存放的媒体**（正式成片等），永不自动清理。首个归档：archive/比亚迪T5使用教程/
- 想保留某条测试片超过 14 天：把它移进 `archive/` 即可

## 没装的（及原因）

- **baoyu-design 全套**：不是视频工具——是幻灯/设计画布/设计系统/仪表盘的本地编辑器技能包，和本环境自带 artifact 能力重合。只取了 dataviz。
- **Remotion**：与 HyperFrames 同层重合；且许可非开源（>3 人公司收费）。除非以后明确要 React 模板生态再加。
- **Motion Canvas / Revideo**：维护基本停滞，不入新栈。
- **Manim**：只适合纯数学推导动画；huashu 的 3b1b 语法已覆盖「像 3b1b 的解说片」，真数学证明再单独装。
- **jianying-editor-skill**（网传的技能封装）：原仓库已 404，只剩小 fork，不装来历不明的；直接用 pyJianYingDraft 本体（已验证）。

## 管线（每支片都走）

1. 定规格：横 1920×1080 / 竖 1080×1920、30fps、时长、要不要口播
2. 镜头表：每镜一行（主体｜动作｜镜头｜屏上字≤8字），开头 3 秒是具体场景不是标题卡；全片一套画风一套色板
3. 文案/口播稿先行（中文约 4 字/秒）
4. 配音（原生 TTS）→ 字幕（按稿对齐或 whisper 转写）
5. 逐镜渲染（huashu 或 HyperFrames 二选一）→ scripts/assemble.py 拼接+混音+烧字幕
6. 质检：抽帧查文字出界/空画面/画风漂移；huashu 路线过 qa.py + deliver.py 门禁
7. 交付：output/<项目>/ 成片 MP4 + 制作说明；要精修再出剪映草稿

## 验证记录（2026-10-31）

- huashu 参数化片段（动态文字语法）渲染成功：7.5s 1080p
- 演示成片：上述片段 + 原生 TTS 配音 + 烧录字幕 → tests/2026-10-31/demo_成片.mp4（5.8s，抽帧质检通过；原在 output/，2026-11-01 按目录约定迁移）
- pyJianYingDraft 生成草稿成功：test-drafts/demo_from_workflow（视频轨+文字轨）
- MoneyPrinterTurbo CLI --help 正常；HyperFrames 实测渲染成功（默认模板 10s 1080p，需 TMPDIR 指到家目录 + HYPERFRAMES_BROWSER_PATH 指到 Playwright 无头 Chrome + GSAP 本地化，jsdelivr 在本网络不可用）
- faster-whisper 实测转写成功（需钉 av<19，模型走 hf-mirror；tiny 仅冒烟，正式用 base+）
- 已知不可用：edge-tts（本 VM 代理掐 WebSocket，在 Windows 本机可用）

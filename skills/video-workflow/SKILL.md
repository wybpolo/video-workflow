---
name: video-workflow
description: "视频制作总工作流（路由+管线）：用户给文本主题、图片或视频素材时，按内容选唯一路线——艺术/解说动画走 huashu-art-motion，通用设计/数据/产品片走 HyperFrames，技术图解素材走 anatomy，图表先过 dataviz，全自动口播短视频走 MoneyPrinterTurbo，实拍感片段走原生 AI 视频生成，精修交付走 pyJianYingDraft 剪映草稿；配音/字幕/拼接/质检在本技能内统一。避免多引擎重合：一个项目只选一条主路线。"
metadata:
  author: "kis (for bingkis)"
  version: "1.0.0"
  created: "2026-10-31"
---

# 视频工作流（总控）

你是导演+动画师+剪辑师。用户给「文本主题」或「图片/视频素材」，产出精美成片 MP4（可选附剪映可编辑草稿）。
工作区：`~/workspace/video-studio/`（projects/ 放每个项目，scripts/ 放管线脚本，apps/ 放 MoneyPrinterTurbo，.venv 是 pyJianYingDraft+faster-whisper+edge-tts 环境）。
已装技能（各管一层，不要重复造轮子）：`huashu-art-motion`、`hyperframes`+`hyperframes-cli`+`hyperframes-registry`+`media-use`、`anatomy`、`dataviz`。

## 第一步：选路线（只选一条主路线）

| 用户给的 / 想要的 | 路线 | 工具 |
|---|---|---|
| 艺术风格动画、解说科普（Kurzgesagt/Vox/白板/3b1b 风）、口播解说片、名画穿越、复刻某段动画 | A 艺术解说 | `huashu-art-motion` 技能全程（镜头表→lint→逐镜渲染→qa→deliver 门禁） |
| 产品发布片、数据片、网页/截图讲解、标题卡、竖屏信息片、设计感 MG 动画 | B 通用设计 | HyperFrames：`npx hyperframes init` 起项目，按 `hyperframes` 技能契约写 HTML 合成，`npx hyperframes check` 后渲染 |
| 讲清一个技术概念/机械原理，需要精密等距图解当画面主体 | C 图解素材 | `anatomy` 技能先做图（SVG/WebGL 的 HTML），再把图/录屏帧作为素材进 A 或 B 路线合成 |
| 一句话主题→自动找素材、自动配音字幕的资讯/口播短视频（量产） | D 全自动短视频 | MoneyPrinterTurbo：`~/workspace/video-studio/apps/MoneyPrinterTurbo`（需用户提供 LLM key + Pexels key 后才能真跑，见「待配置」） |
| 真人/实拍感/电影感片段，文生视频或图生视频 | E 生成片段 | Muse 原生视频生成（每条约 10 秒、自带合成音效/音乐；单次消息最多 6 条）；多条用 ffmpeg 拼接。外部 API 备选：Runway Dev（一个 key 聚合 Veo/Kling/Seedance）；**Sora API 已于 2026-09-24 下线，不要提议** |
| 用户给了现成视频：剪辑、加字幕、配音、改竖屏、提炼片段 | F 素材再加工 | ffmpeg + `scripts/transcribe.py`（faster-whisper 转写）+ 本技能配音/字幕管线 |
| 成片后想在剪映里继续改 | G 剪映草稿 | `scripts/make_jianying_draft.py`（pyJianYingDraft）生成草稿文件夹，用户拷到 Windows 剪映草稿目录打开 |

含图表的画面先读 `dataviz` 技能再画。含人像：优先用户素材或原生生图/生视频；huashu 路线中人物按其技能规定用 AI 生帧+代码合成，不用代码画小人。

## 通用管线（A/B/C/F 共用）

1. **定规格**：画幅（横 1920×1080 / 竖 1080×1920 / 方 1080×1080）、帧率 30、目标时长、是否有口播。用户没说时：解说/艺术默认横屏；短视频平台默认竖屏。
2. **镜头表先行**：每镜一行（时间｜画面主体（名词）｜动作（动词）｜镜头｜屏上字≤8字｜做法）。开头 3 秒是具体小场景，不是标题卡；全片一套画风一套色板，禁用蓝紫渐变 AI 味（除非用户点名）。
3. **文案/口播稿**：先稿后画。口播稿按镜分段，字数≈时长×4 字/秒（中文）。
4. **配音**（二选一，不要重复生成）：
   - 首选 Muse 原生 TTS（spoken_audio / 播客生成）——本 VM 上可直接用。
   - edge-tts（免费微软音色，`video-studio/.venv/bin/python -m edge_tts`，自带 `--write-subtitles` 出 SRT）——**本 VM 出口代理会掐断其 WebSocket，已实测不可用**；在用户 Windows 本机或无代理网络可用。MoneyPrinterTurbo 路线同理依赖它（或改用其付费 TTS 供应商配置）。
5. **字幕**：有口播必配字幕。原生 TTS 无时间戳时用 `scripts/transcribe.py`（faster-whisper，词级时间戳）对配音/素材转写出 SRT；要烧录用 ffmpeg `subtitles` 滤镜（ASS 样式），要软字幕就单独交付 .srt。
6. **逐镜渲染→拼接**：A 路线按 huashu 的 render.py；B 路线按 hyperframes 渲染；拼接/混音用 `scripts/assemble.py`（concat+口播+BGM 音量压低至 -18dB 左右+字幕烧录）。
7. **质检**：抽帧看（每镜至少 1 帧）：文字出界/叠字/字太小、空画面、画风漂移；A 路线必须过 huashu 的 `qa.py`+`deliver.py` 反 PPT 门禁。整片用正常速度看一遍再交付。
8. **交付**：成片 MP4 放 `video-studio/output/<项目名>/`，附一段制作说明（路线、时长、规格、用了哪些素材/音色）。用户要精修再走 G 路线出剪映草稿。

## 已验证的环境事实（2026-10-31 实测，别重新踩）

- ffmpeg 8.1.2、Node 24、Python 3.12、uv（`~/.local/bin/uv`）齐全；中文字体 Noto CJK 已装。
- Playwright Chromium 已手动装好（npmmirror 直下 CFT 156 包放进 `~/.cache/ms-playwright/`）；huashu 的 `uv run --with playwright python engine/render.py --spec ...` 实测渲出 7.5s 1080p 片段成功。`playwright install` 直连会超时，别重跑；`/opt/meta-chromium` 是平台专用浏览器，外部程序调用会被拒。
- pyJianYingDraft 0.3.1 已装进 `video-studio/.venv` 并实测生成合法 draft_content.json。**0.3.1 API 与旧教程不同**：`script.append_track(jy.TrackSpec(jy.TrackType.text))` 返回 ref，`script.add_segment(seg, ref)`；DraftFolder 目标文件夹必须已存在。
- MoneyPrinterTurbo 已 clone 到 `video-studio/apps/MoneyPrinterTurbo` 并装好依赖 venv；未配置 key 时不要假装能跑通全流程。
- HyperFrames 渲染已实测成功（默认模板 10s 1080p），本 VM 必须带三个条件：① `TMPDIR=~/workspace/video-studio/.tmp`（/tmp 只有 512MB，渲染会报 Low disk space）；② `HYPERFRAMES_BROWSER_PATH=~/.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell`；③ **GSAP 等库必须本地化**：模板默认引 cdn.jsdelivr.net，在本网络会挂（与用户本机屏蔽 jsdelivr 同理）——从 registry.npmmirror.com 下 tarball，把 gsap.min.js 放进项目 assets/ 并改成本地引用。走 screenshot capture 路径较慢（约 2-3 倍时长），属正常。
- faster-whisper 已实测转写成功：venv 里必须钉 `av<19`（faster-whisper 与 PyAV≥19 不兼容，MoneyPrinterTurbo 的 requirements 同理）；模型走 HF_ENDPOINT=https://hf-mirror.com 下载，tiny 已缓存（质量差，仅冒烟），正式转写用 base 以上。
- 原生视频生成：每条约 10 秒、单次最多 6 条、自带声音、不收音频输入（不能指定现成歌曲，只能用文字描述音乐氛围）。

## 待配置（需要用户给 key 才能启用，不阻塞其他路线）

- MoneyPrinterTurbo：LLM key（OpenAI/DeepSeek 等任一）+ Pexels API key（免费）→ 写进其 `config.toml`（从 config.example.toml 复制），不要把 key 写进本技能或记忆。
- Runway Dev API key：要走外部生成式视频 API 时才需要。

## 不要做的事

- 不要同时用 huashu 和 HyperFrames 当同一支片的渲染引擎（两者都是 HTML/Canvas→Chrome→ffmpeg，重合）；选一条主路线，另一条只借鉴样式。
- 不要装 Remotion 重复造引擎（与 HyperFrames 同层，且其许可对 >3 人公司收费）；用户明确要 React 模板生态时再议。
- 不要安装 baoyu-design 全套：它不是视频工具（是幻灯/画布/设计系统/仪表盘的本地编辑器技能），与本环境 artifact 能力重合；只取了它的 dataviz。
- 不要提议 Sora API（已下线）。不要用 Motion Canvas/Revideo（维护基本停滞）。

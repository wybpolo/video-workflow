---
name: video-workflow
description: "视频制作总工作流（路由+管线）：用户给文本主题、图片或视频素材时，按内容选唯一路线——艺术/解说动画走 huashu-art-motion，通用设计/数据/产品片走 HyperFrames，技术图解素材走 anatomy，图表先过 dataviz，全自动口播短视频走 MoneyPrinterTurbo，实拍感片段走原生 AI 视频生成，小说/故事改短剧走 shuohao 短剧流水线，给参考视频要翻拍/复刻/批量变体走参考复刻法，精修交付走 pyJianYingDraft 剪映草稿；配音/字幕/拼接/质检在本技能内统一。避免多引擎重合：一个项目只选一条主路线。"
metadata:
  author: "kis (for bingkis)"
  version: "1.3.0"
  created: "2026-10-31"
---

# 视频工作流（总控）

你是导演+动画师+剪辑师。用户给「文本主题」或「图片/视频素材」，产出精美成片 MP4（可选附剪映可编辑草稿）。
工作区：`~/workspace/video-studio/`（projects/ 放每个项目，scripts/ 放管线脚本，apps/ 放 MoneyPrinterTurbo，.venv 是 pyJianYingDraft+faster-whisper+edge-tts 环境）。
已装技能（各管一层，不要重复造轮子）：`huashu-art-motion`、`hyperframes`+`hyperframes-cli`+`hyperframes-registry`+`media-use`、`anatomy`、`dataviz`、短剧流水线 `novel-outline`/`novel-characters`/`novel-art`/`novel-script`/`novel-staging`/`novel-storyboard`/`character-refs`（shuohao-skills，Apache-2.0，锁定 commit 见仓库 UPSTREAM.md）、动效词典 `motion-prompt`（参考层，不占路线）、`ffmpeg-skill`（F 路线契约化工具层，MIT）、`pixelfx`（像素特效资产层，MIT）、`manimgx`（C 路线数学/3D 引擎技能，引擎按需 pip 装，MIT）、`vibe-knowledge-film`（A 路线无旁白知识长片子技能，MIT）。风格参考库在本技能 `references/` 下：`lemo-styles/`（lemo-opuscar 的 67 份电影风格语法 STYLE.md，CC BY 4.0）、`mg-styles/`（mg-styles-15 的 15 份整片风格提示词 + rubric 评审法 + template，MIT）。上游锁定 commit 见仓库 UPSTREAM.md。

## 第一步：选路线（只选一条主路线）

| 用户给的 / 想要的 | 路线 | 工具 |
|---|---|---|
| 艺术风格动画、解说科普（Kurzgesagt/Vox/白板/3b1b 风）、口播解说片、名画穿越、复刻某段动画 | A 艺术解说 | `huashu-art-motion` 技能全程（镜头表→lint→逐镜渲染→qa→deliver 门禁）。子格式：无旁白、字幕驱动的横屏知识长片（2–5 分钟，抖音「知识大赏」式）走 `vibe-knowledge-film` 技能（见下「方法规范」A 子路线） |
| 产品发布片、数据片、网页/截图讲解、标题卡、竖屏信息片、设计感 MG 动画 | B 通用设计 | HyperFrames：`npx hyperframes init` 起项目，按 `hyperframes` 技能契约写 HTML 合成，`npx hyperframes check` 后渲染 |
| 讲清一个技术概念/机械原理，需要精密等距图解当画面主体 | C 图解素材 | `anatomy` 技能先做图（SVG/WebGL 的 HTML），再把图/录屏帧作为素材进 A 或 B 路线合成。真数学/3D（LaTeX 公式逐步变形、3D 曲面、动力系统）走 `manimgx`（Manim 兼容 API + Rust 引擎，本 VM 用 lavapipe CPU 渲染）；像素风特效素材（火/爆炸/魔法/天气/转场 wipe）走 `pixelfx` 出帧序列或 sprite sheet 再进合成 |
| 一句话主题→自动找素材、自动配音字幕的资讯/口播短视频（量产） | D 全自动短视频 | MoneyPrinterTurbo：`~/workspace/video-studio/apps/MoneyPrinterTurbo`（需用户提供 LLM key + Pexels key 后才能真跑，见「待配置」） |
| 真人/实拍感/电影感片段，文生视频或图生视频 | E 生成片段 | **默认生成后端 = Muse 原生视频生成（免 key）**（每条约 10 秒、自带合成音效/音乐；单次消息最多 6 条）；多条用 ffmpeg 拼接。外部 API 仅作可选占位：Runway Dev（一个 key 聚合 Veo/Kling/Seedance），无 key 时不提议；**Sora API 已于 2026-09-24 下线，不要提议** |
| 用户给了现成视频：剪辑、加字幕、配音、改竖屏、提炼片段 | F 素材再加工 | 默认用 `ffmpeg-skill` 的契约脚本（probe 先行→`--dry-run` 出计划→执行→`check.py --platform` 按平台规格验收），手写 ffmpeg 只作兜底；转写仍走 `scripts/transcribe.py`（faster-whisper）+ 本技能配音/字幕管线 |
| 成片后想在剪映里继续改 | G 剪映草稿 | `scripts/make_jianying_draft.py`（pyJianYingDraft）生成草稿文件夹，用户拷到 Windows 剪映草稿目录打开 |
| 小说/故事/梗概改编短剧、连续剧集、真人角色出演的剧情片 | H 短剧生产 | shuohao 流水线（见下「H 路线」专节）：大纲→角色/美术/剧本→走位→分镜生成包→E 路线生成→通用管线成片 |
| 给一条参考视频（爆款/广告/带货/口播），要翻拍复刻、换人换物、或批量做变体 | I 参考复刻 | 纯方法路线（见下「I 路线」专节）：F 路线拆解结构→结构卡→E 路线按结构生成→通用管线出变体；不装任何外部平台 |

含图表的画面先读 `dataviz` 技能再画。含人像：优先用户素材或原生生图/生视频；huashu 路线中人物按其技能规定用 AI 生帧+代码合成，不用代码画小人。
写运镜/动效/转场的提示词或指令时，可查 `motion-prompt` 词典（动效与カメラワーク的命名+活样例库）取准确名称与规格，不要自己生造词。

## 方法规范与参考层（v1.3.0 吸收，不占路线）

以下方法来自 2026-11-01 对 14 个开源项目的深读评估（产物在 `~/workspace/video-research/eval2/`）。它们是规范与参考，不是新引擎——写片时按所属路线取用，不要为它们另起管线。

- **风格参考层**：选风格/定调时先翻三处——`motion-prompt`（单个动效级词典）、本技能 `references/lemo-styles/`（67 种电影风格语法：不变量+禁忌清单，A/B 定调用）、`references/mg-styles/`（15 种整片 MG 风格的完整提示词，换种子出新片；其 `rubric.md` 的双 AI 两轮评审法可用于成片自评）。
- **解说方法**（吸收自 anything2explainer + video-talkcraft）：①解说词先行且先给用户确认，再做画面；②长片先渲 30 秒样片过关再铺全片；③量化 QC：最长静止画面 ≤3s；④字级对时：配音定稿后用 whisper 字级时间戳把关键动效锁在词上，不靠估时；⑤反 PPT：运动做减法、一拍一主角，不堆贴纸与装饰。
- **B 路线质检与音频**（吸收自 motion-video-kit + motionmaxxing）：交付前过可测量门——冻结帧时长、响度 LUFS、对比度、品牌色一致（motion-video-kit 的 quality-bar/audio 原文在 eval2 克隆里，可借用其脚本）；音频规则：有真实曲目时倒排让结尾落在片尾卡，音效增益按频段解算；反 slop 清单（禁用模式）：角落小标签、数字计数器、左标题右卡片式模板排版、无意义的装饰性动效。
- **作曲模式**（吸收自 huashu-motion）：需要原创 BGM 又不想用素材库时，可走「先写谱（简谱/ABC 思路）→ 本机采样或合成演奏 → 切点对齐节拍排镜头」，补 BGM 空白；其「可编辑变量 + data-id 指帧定点返修」可借给 B 路线项目做返修规范（关键元素留 id，返修只改点名处）。
- **A 子路线·无旁白知识长片**（`vibe-knowledge-film` 技能）：讲解设计优先于画面——每个概念先找一个外行认得的「形象」把它演出来（动词真的发生，不用点线圈代替），文案即字幕与分镜同写；先 30 秒样片、终检有量化门槛。仅 16:9 横屏，与 huashu 的有旁白短解说互补不冲突。

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

## PPT / 文档转视频（实证流程，2026-10-31 比亚迪 T5 教程 4分30秒成片跑通）

用户给 PPT/PDF 手册类素材做教程片时走 B 路线，按下面顺序做，每条都是这次踩过或验过的：

1. **拆解**：PyMuPDF（`uv run --with pymupdf`）双路提取——逐页渲染图（110dpi，看版式）+ 提取内嵌原图（≥500px 才留）。先把候选图拼 contact sheet 肉眼选材和对位（哪张图配哪节内容），再动设计。PPT 页渲染图只用于理解，**绝不整页当画面**（那是翻页 PPT，不是视频）；用提取的原图/编号图解进重新设计的场景。
2. **核事实**：手册/PPT 内部数据常有占位（「待补充」）和版本对位错误（这次车型代码与电量三页互相矛盾）。关键数字必须与公开来源交叉核对，矛盾处取多源一致值，并把取舍留在项目记录里。
3. **先配音、后定时**（最重要）：按场景切口播稿 → 逐场 TTS → ffprobe 实测每场时长 → 场景时长 = 0.4s 头垫 + 配音 + 0.9s 尾垫，累加得全片时间轴。配音轨用 ffmpeg 把「静音+配音+静音」逐场拼接，与画面天然对齐；字幕按句切分、按字数比例分配场内时间（44 条字幕实测可用），比 whisper 转写更快更准（稿子就是原文）。
4. **生成器模式**：十场以上的片子不要手写 HTML——写一个 gen.py（场景内容用数据结构描述），一次生成 index.html + plan.json + SRT + 配音拼接命令。改版式只改生成器重跑，时间轴永远以实测配音为准。
5. **字幕安全区**：烧录字幕占底部约 130px。所有卡片/图注必须收在 y≈920 以上；封面底部数据条、右列最后的提示卡是最容易被字幕压住/裁掉的两处（这次首检三处缺陷全在这里）。纵向列排版先估总高再落位。
6. **大数字排版**：核心数字单独成行 + `white-space:nowrap`，单位/区间放标签行；「30%→80% ≈18分钟」这类长串同行必折行毁版。
7. **长片分段视觉**：单场配音 >30s 时场内做两段视觉相位（如充电→保养），在配音约 52% 处交叉淡化切换，避免一幅画面挂到底。
8. **质检闭环**：渲染后抽每场中点帧 + 相位切换点帧，拼图总览逐项看（压字/裁切/折行/空场），修完重渲再抽查修改场。这次一轮修复解决全部缺陷，不要省这一轮。

## H 路线：短剧生产流水线（shuohao-skills）

总控只定顺序与交接，方法论在各技能内，不要在总控复述。阶段与产物（每阶过自带脚本质量门再往下走）：

1. `novel-outline`：小说/故事 → 改编大纲（outline.json：改编说明、角色表、节拍、分集梗概、资产清单）。
2. 三件并行迭代：`novel-characters`（角色圣经：设定图提示词、声线提示词、model sheet）、`novel-art`（美术圣经：场景与叙事道具的一致性锚点、白底空景）、`novel-script`（剧本：动作节拍与台词交替、按语速确定性估时长、前 3 拍冷开场钩子、角色台词本直喂 TTS）。
3. `character-refs`（可独立用）：以一张正面全身图为锚点，生成角色多视图参考图（头像/90° 侧面/背面/细节），给分镜与生成阶段锁人物一致性。生成后端按其技能说明选（本机默认走 Muse 原生生图当 custom 后端）。
4. `novel-staging`：按剧本+场景图排每场开场走位（站位/朝向/在场），产 staging.json 与走位句。
5. `novel-storyboard`：分镜 + 逐镜生成提示词（Seedance 2.0 / MiniMax H3 规格，含 shot-writing 规范）。
6. **生成交接**：分镜提示词默认喂 Muse 原生视频生成（E 路线，免 key）——其镜头描述与台词结构可直接用；要上 Seedance/H3 原生平台出片时，由用户在即梦/海螺端生成后回传，走 F/拼接管线。角色一致性靠 character-refs 锚点图做图生视频首帧。
7. 成片走通用管线：台词本→TTS 配音（或生成片段自带声）、字幕、拼接、质检。默认竖屏 1080×1920。

## I 路线：参考复刻（吸收 hypit 方法，不装其平台）

hypit（27k★）是整套独立生产系统（自有语言/运行时/供应商），与 B 路线+拼接管线全面重合，只取其「复刻」方法，用现有工具执行：

1. **拆解**（F 路线工具）：参考片转写（faster-whisper）+ 按镜头抽帧 + 逐镜标注：钩子（前 3 秒）、结构段（钩子→展示→卖点/反转→收尾 CTA）、每镜景别/运镜/时长、台词骨架、字幕与 BGM 位置。产出一张「结构卡」（JSON 或 md 存项目目录）。
2. **变量表**：把可替换项列清——人物（脸/服装/声线）、物品（产品/道具）、台词（卖点词）、场景、B-roll；不变的是结构与节奏。
3. **复刻生成**：按结构卡逐镜走 E 路线（Muse 原生生成，免 key）出新片段；真人一致性需求高时先用 character-refs 做锚点图再图生视频。运镜词查 motion-prompt。
4. **变体量产**：同一结构卡换变量表即出一支新变体；每支过通用管线（配音/字幕/拼接/质检）。先出 1 支样片给用户确认，再批量。
5. 边界：只复刻结构与表现形式，不逐帧抄袭受版权保护的成片内容；换脸指向真实公众人物时需用户明确授权素材。

## 已验证的环境事实（2026-10-31 实测，别重新踩）

- ffmpeg 8.1.2、Node 24、Python 3.12、uv（`~/.local/bin/uv`）齐全；中文字体 Noto CJK 已装。
- Playwright Chromium 已手动装好（npmmirror 直下 CFT 156 包放进 `~/.cache/ms-playwright/`）；huashu 的 `uv run --with playwright python engine/render.py --spec ...` 实测渲出 7.5s 1080p 片段成功。`playwright install` 直连会超时，别重跑；`/opt/meta-chromium` 是平台专用浏览器，外部程序调用会被拒。
- pyJianYingDraft 0.3.1 已装进 `video-studio/.venv` 并实测生成合法 draft_content.json。**0.3.1 API 与旧教程不同**：`script.append_track(jy.TrackSpec(jy.TrackType.text))` 返回 ref，`script.add_segment(seg, ref)`；DraftFolder 目标文件夹必须已存在。
- MoneyPrinterTurbo 已 clone 到 `video-studio/apps/MoneyPrinterTurbo` 并装好依赖 venv；未配置 key 时不要假装能跑通全流程。
- HyperFrames 渲染已实测成功（默认模板 10s 1080p），本 VM 必须带三个条件：① `TMPDIR=~/workspace/video-studio/.tmp`（/tmp 只有 512MB，渲染会报 Low disk space）；② `HYPERFRAMES_BROWSER_PATH=~/.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell`；③ **GSAP 等库必须本地化**：模板默认引 cdn.jsdelivr.net，在本网络会挂（与用户本机屏蔽 jsdelivr 同理）——从 registry.npmmirror.com 下 tarball，把 gsap.min.js 放进项目 assets/ 并改成本地引用。走 screenshot capture 路径较慢（约 2-3 倍时长），属正常。
- faster-whisper 已实测转写成功：venv 里必须钉 `av<19`（faster-whisper 与 PyAV≥19 不兼容，MoneyPrinterTurbo 的 requirements 同理）；模型走 HF_ENDPOINT=https://hf-mirror.com 下载，tiny 已缓存（质量差，仅冒烟），正式转写用 base 以上。
- HyperFrames 长片（270s/8117 帧）实测：截图捕获约 2.6 倍片长（≈12 分钟），属正常，别中途杀。**渲染进程 exit 0 ≠ 文件完好**：曾出现输出 MP4 只有 mdat 没有 moov（被截断在整 22MiB 处）——渲染后必须 ffprobe 验时长/流再继续；失败时删掉项目下的 `work-*` 与 `.film_*.hf-transaction-*` 残留再重渲。`hyperframes check` 顶层报 failed 时先看 lint 明细：0 error 只有 warning（多场单文件、嵌套结构）可正常渲染。
- HyperFrames 字体：CSS 里写 CJK 字体名必须配本地 @font-face，否则 check 直接 error 且渲染回退默认字体。本机做法：fonttools+brotli 从 `/usr/share/fonts/opentype/noto/NotoSansCJK-{Regular,Bold}.ttc` 取 SC 面（fontNumber=2）转 woff2（各约 11MB）放项目 assets/fonts/，@font-face 按 400/700/800 声明。转换约需 3 分钟，放后台跑。
- 原生视频生成：每条约 10 秒、单次最多 6 条、自带声音、不收音频输入（不能指定现成歌曲，只能用文字描述音乐氛围）。
- **原生生成可带对白（2026-11-01 实测）**：把台词逐字写进提示词并指明说话人、声线与语言（如「speaking angrily in Mandarin: "…"」），模型会按角色发声、口型同步，多人对话可逐句分配。短剧/剧情片优先走原生对白——TTS 后配既对不上口型，本机 TTS 又只有单一默认音色（女角配出男声、变调老人声怪异，都是实测教训）。生成后必须用 faster-whisper 转写核对台词（同音字误听靠字幕按剧本校正），并按转写时间轴排字幕。每镜台词控制在 2 句内，长台词拆镜。

## 待配置（需要用户给 key 才能启用，不阻塞其他路线）

- 生成后端默认 Muse 原生（免 key），以下均为可选占位，不配不影响 H/I/E 路线运转：
  - Runway Dev API key：想直连 Veo/Kling/Seedance 聚合 API 时才需要。
  - Seedance（火山/即梦）或 MiniMax H3 平台账号：想按 shuohao 分镜的原生规格出片时才需要；否则原生生成顶替。
  - 本地 GPU 跑 H3 不采用：FreeVideo（本地推理，最低 8GB 显存）已评估，用户 2026-11-01 明确决定不依赖本地 GPU，不要再提议装它；H3 原生规格只走云端通道。
- MoneyPrinterTurbo：LLM key（OpenAI/DeepSeek 等任一）+ Pexels API key（免费）→ 写进其 `config.toml`（从 config.example.toml 复制），不要把 key 写进本技能或记忆。

## 不要做的事

- 不要同时用 huashu 和 HyperFrames 当同一支片的渲染引擎（两者都是 HTML/Canvas→Chrome→ffmpeg，重合）；选一条主路线，另一条只借鉴样式。
- 不要装 Remotion 重复造引擎（与 HyperFrames 同层，且其许可对 >3 人公司收费）；用户明确要 React 模板生态时再议。
- 不要整装 anything2explainer / video-talkcraft：两者都是 PolyForm 非商业许可 + Remotion 引擎，与 A/B 同层；方法已吸收进下文「方法规范与参考层」，配方卡只借分类法、不复制其代码进生产。
- 不要整装 huashu-motion / animate / motionmaxxing / openfilm：huashu-motion 是 huashu-art-motion 的同作者姊妹产品（产品发布片工作室），不是升级版、不要替换；animate 与 A 全重合且成熟度浅；motionmaxxing 自带第二套渲染运行时；openfilm 的价值在本地 GUI 编辑器，云端 VM 落不了地。各自可取的方法已吸收。
- 不要安装 baoyu-design 全套：它不是视频工具（是幻灯/画布/设计系统/仪表盘的本地编辑器技能），与本环境 artifact 能力重合；只取了它的 dataviz。
- 不要提议 Sora API（已下线）。不要用 Motion Canvas/Revideo（维护基本停滞）。
- 不要安装 hypit 平台：它是整套独立生产系统（SVML 语言+运行时+供应商体系），与 HyperFrames+拼接管线重合，其技能壳脱离运行时无用；复刻方法已吸收进 I 路线。用户明确要换脸级复刻或百条级量产时，再按「独立 app」单独评估（参照 MoneyPrinterTurbo 的装法），不要塞进技能路由。
- 不要把 shuohao 各阶段的方法论抄进总控技能：总控只写阶段顺序、产物与交接点，细节永远以各 novel-* 技能原文为准，避免双份维护。

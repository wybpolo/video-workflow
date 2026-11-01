# Changelog

## v1.3.1 — 2026-11-01

文档与经验沉淀（无技能/路由变更）：

- **README 新增「生成后端与环境差异」**：写明 muse.ai 环境内视频/图片生成是内置原生能力、免 key 可用（且图片生成应善用于角色锚图/分镜参考图等素材补位）；外部环境没有内置生成，必须自备服务商接口地址 + key，未配置时 E/H/I 只能先做到分镜与提示词。路线表同步补齐 H/I 与 v1.3.0 新技能。总控技能「已验证的环境事实」补同一条。
- **examples/demo 扩为实战经验库**：新增四篇——BYD T5 PPT 转视频（长渲染验完整性、数字出入标注拍板）、《凌晨两点的花》短剧 v1→v2（原生对白标准做法与四个坑）、参考复刻（结构卡/变量表方法）、v1.3.0 四技能实测速记（各自上手要点与实测坑）；原 v1.0.0 演示基线保留并入索引。
- **本地 studio 媒体目录约定**（见 studio/README）：测试片/示例片统一存 `video-studio/tests/<YYYY-MM-DD>/`，每周定时清理超过 14 天的（scripts/cleanup_tests.sh + 每周任务）；长期媒体存 `archive/`；正式工程留 `projects/`、交付落点 `output/`。存量已迁移：演示与验证片进 tests/2026-10-31 与 tests/2026-11-01,比亚迪 T5 成片进 archive/。

## v1.3.0 — 2026-11-01

第二批 14 个开源项目深读评估后的集成（逐仓结论见总控技能与本地评估记录）：

- **新增 4 技能**：ffmpeg-skill（锁定 1ce2c18）——F 路线工具层换装为契约流程（probe→dry-run 计划→执行→check 平台规格验收）；pixelfx（a841596）——像素特效资产层（244 个代码特效，零依赖）；manimgx（技能文件锁定 1fb4dd7，引擎 uv 装 PyPI 0.1.1）——C 路线数学/3D 精密引擎（LaTeX 公式变形、真 3D；VM 无 GPU 时 lavapipe CPU 渲染实测可用）；vibe-knowledge-film（62d5150）——A 路线子路线：无旁白、字幕驱动的横屏知识长片
- **参考层摘录**进总控 references/：lemo-opuscar 的 67 份电影风格语法 STYLE.md（bebbbe1，CC BY 4.0）+ mg-styles-15 的 15 份整片风格提示词与 rubric 双 AI 评审法（49052d8)，与 motion-prompt（单动效级）粒度互补
- **总控新增「方法规范与参考层」**（只吸收方法、不装引擎）：解说方法（文案先行且先确认、30 秒样片门、量化 QC、whisper 字级对时、反 PPT——源自 anything2explainer + video-talkcraft，两者 PolyForm 非商业 + Remotion，禁止整装）；B 路线可测量质检与音频规则 + 反 slop 清单（motion-video-kit + motionmaxxing）；作曲模式与 data-id 指帧返修契约（huashu-motion——与 huashu-art-motion 是同作者姊妹产品，不是升级版，不替换）
- **不采用补明**：FreeVideo 本地 H3 后端不装（用户决定不依赖本地 GPU；H3 原生规格只走云端通道）；openfilm/animate 跳过（同层重合/落地形态不合）
- **四条示例片验证**（本地 video-studio/projects/eval2-demos/，不入库）：ffmpeg-skill 截《凌晨两点的花》v2 做响度归一过 TikTok 验收（−14.02 LUFS、14 项全过）；pixelfx 六类特效展示片（24s 720p，全部一次渲通）；manimgx 《傅里叶级数逼近方波》（720p 引擎渲染 22.5s，进程映射实锤 lavapipe）；vibe 《为什么冰会浮》30 秒样片（走完其 0–9 步流程，字体经其预留槽位用本地 Noto 顶替，−18.37 LUFS 对上其 C 世界规格）

## v1.2.0 — 2026-11-01

新增短剧与复刻两条路线（用户点名评估的三个外部工作流，克隆实读后集成）：

- **H 短剧生产**：shuohao-skills 全套 7 技能 vendored（锁定 5612d2a，Apache-2.0）——novel-outline/characters/art/script/staging/storyboard + character-refs，自带脚本质量门，自测实测通过（336+154 项）
- **I 参考复刻**：hypit 不装平台（整套独立系统与 B 路线+管线重合），只吸收其复刻方法写成纯方法路线：拆解结构卡→变量表→E 路线生成→变体量产
- motion-prompt 轻量 vendored（3 文件 68K，锁定 7819d38）：动效/运镜命名词典，作横切参考层，不占路线
- 生成后端定版：E/H/I 默认 Muse 原生视频生成（免 key），Runway Dev 降为可选占位
- **原生对白实证**（两条示例片验证）：台词逐字写进生成提示词并指明说话人/声线/语言，模型按角色发声且口型同步，生成后 whisper 转写核对、按转写轴排字幕；短剧优先原生对白，不再 TTS 后配（本机 TTS 单一默认音色会女角男声、变调老人声怪异）。每镜台词 ≤2 句
- 示例片验证：H 路线原创微短剧《凌晨两点的花》EP1（v1 配音版 48s + v2 原生对白冲突版 48.5s，大纲/剧本/分镜全过质量门，唯一例外是连续剧结构门对单集天然无解）；I 路线 Pexels 参考片拆结构卡并复刻出男士面霜/梳妆台唇膏两支变体 + 对比片

## v1.1.0 — 2026-10-31

首次真实生产（比亚迪 T5 教程，4分30秒 1080p）经验回写：

- 总控技能新增「PPT / 文档转视频」实证流程（8 条）：PyMuPDF 双路拆解 + contact sheet 选材、关键数字多源核对、先配音后定时的场景时间轴（0.4+实测+0.9）、按句比例字幕、gen.py 生成器模式、字幕安全区（内容收在 y≈920 以上）、大数字 nowrap 排版、长场双相位、抽帧质检闭环
- 环境事实补三条：HyperFrames 长片渲染约 2.6 倍片长且 exit 0 也可能截断（必须 ffprobe 验文件、清 work-*/.hf-transaction-* 残留重渲）；check 顶层 failed 先看 lint 明细（0 error 可渲）；CJK 字体必须本地 @font-face（fonttools 从 Noto TTC 取 SC 面转 woff2 的做法）

## v1.0.0 — 2026-10-31

首个版本：调研选型 + 全路线实测打通后建仓。

- 总控技能 video-workflow（A–G 七条路线、通用管线、环境事实、禁区清单）
- vendored 技能：dataviz（全量）、HyperFrames 官方 4 技能（文本部分）
- studio 管线脚本：assemble.py / transcribe.py / make_jianying_draft.py
- install.sh 一键恢复（上游按 UPSTREAM.md 锁定 commit）
- 验证基线：huashu 片段渲染、HyperFrames 渲染、原生 TTS+字幕烧录成片、pyJianYingDraft 草稿、faster-whisper 转写、MoneyPrinterTurbo CLI 均实测通过；edge-tts 在云 VM 不可用（已注明）

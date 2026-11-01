# Changelog

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

# 上游锁定清单（2026-11-07 更新）

install.sh 按下表 commit 拉取/恢复。升级上游时先改这里、验证、再升本仓版本。

| 上游 | 仓库 | 锁定 commit | 许可 | 入库方式 |
|---|---|---|---|---|
| huashu-art-motion | github.com/alchaincyf/huashu-art-motion | 8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c | MIT（部分素材除外，见其仓库） | 不 vendored（74MB，含字体/图片二进制）；install.sh clone 后 checkout |
| anatomy | github.com/wheresryan22/anatomy | 1482e8469b0a9e0d8cc18ea2740a01423d29ae80 | MIT | 不 vendored（27MB，含图片）；install.sh clone 后 checkout |
| HyperFrames 技能 | github.com/heygen-com/hyperframes（skills/ 子目录） | a04b45a6db0d1f724be9cf1985c3b13657195f0d | Apache-2.0 | 文本部分 vendored 在 skills/ 下（已核对 SKILL.md 与该 commit 字节一致）；排除的二进制：hyperframes 的 6 个 .woff2 字体、media-use 的 19 个 .mp3 音效——install.sh 从上游补齐完整目录，覆盖 vendored 副本 |
| dataviz | github.com/JimLiu/baoyu-design（skills/dataviz） | 25f1c06c4d7c6619aa7c3ded96302c9e5f2ac847 | MIT | 全量 vendored（10 个文本文件） |
| shuohao-skills（短剧流水线 7 技能） | github.com/eternityspring/shuohao-skills（skills/ 子目录） | 5612d2a0bd5f19d978c3ee19d1e42840335e3b4b | Apache-2.0 | 文本部分 vendored 在 skills/ 下（novel-outline/characters/art/script/staging/storyboard + character-refs）；排除的二进制：各技能 assets/ 的 report.webp/jpg 报告截图——install.sh 从上游补齐完整目录，覆盖 vendored 副本。各技能自带 selftest 已实测通过（storyboard 336 项、script 154 项） |
| motion-prompt | github.com/showheyohtaki/motion-prompt（skills/motion-prompt） | 7819d3879eb7d5a1475c11c001bedffb5cab64af | MIT | 全量 vendored（3 个文本文件，68K）；画廊 kit 按其 SKILL.md 在使用时从官网获取 |
| ffmpeg-skill | github.com/kajisho5/ffmpeg-skill | 1ce2c186bf1dba96132d87274eee46df4f537e0e | MIT | 文本部分 vendored 在 skills/ffmpeg-skill（284 文件，含其测试套件）；install.sh 从上游补齐完整目录，覆盖 vendored 副本 |
| pixelfx | github.com/patch-gg/pixelfx | a84159688af3ca37a4be05a0d422b94451b2e24e | MIT | 文本部分 vendored 在 skills/pixelfx（310 文件：技能 + src 特效库 + tools + docs）；演示媒体等二进制由 install.sh 从上游补齐 |
| manimgx | github.com/academa-labs/manimgx（skills/manimgx） | 1fb4dd7327bf5ed7d0c40d022c05cb816455ae1d | MIT | 仅技能文件 vendored（1 文件，已与该 commit 字节核对一致）；引擎不入库，install.sh 用 `uv tool install --python 3.14 manimgx` 装（PyPI 0.1.1） |
| vibe-knowledge-film | github.com/HeyChengC/vibe-knowledge-film | 62d51508aad00003dc6209afa80c4b5dc540de59 | MIT | 文本部分 vendored 在 skills/vibe-knowledge-film（40 文件：SKILL + references + engine 代码 + examples 文本）；示例媒体等二进制由 install.sh 从上游补齐 |
| lemo-opuscar（参考层） | github.com/lemomo-ai/lemo-opuscar | bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00 | 代码 MIT / 风格 CC BY 4.0 | **不装技能**：仅 67 份 styles/*/STYLE.md 摘录 vendored 在 skills/video-workflow/references/lemo-styles/ |
| mg-styles-15（参考层） | github.com/Vincentwei1021/mg-styles-15 | 49052d80bfaf9fa8412cc9710530e5e95a3b8d8c | MIT | **不装技能**：仅 prompts/ 15 份 + rubric.md + template.md 摘录 vendored 在 skills/video-workflow/references/mg-styles/ |
| hypit | github.com/hypit-ai/hypit | —（不锁定） | 修改版 Apache-2.0（附加条件） | **不安装**：整套独立生产系统与本仓管线重合；其参考复刻方法已吸收为总控 I 路线（纯方法，零代码） |
| MoneyPrinterTurbo | github.com/harry0703/MoneyPrinterTurbo | 8dbfbb8e9de1b8f9d745d73a8e9f07464248cdd9 | MIT | 不 vendored（独立应用）；install.sh clone 到 video-studio/apps 并装 venv |
| multiplane | github.com/LBEILC/Multiplane | e20b8451703a4ecfd79ca41f380b9d79d2fb926f | Apache-2.0 | 仅技能文件 vendored（1 文件，skills/multiplane）；引擎不入库，install.sh clone 后 rsync 到 video-studio/apps/multiplane 并 npm install |
| rea-video | github.com/JuneYaooo/rea-video | c9359c46f90c9824713081ea18fd207a45a0636a | Apache-2.0 | 技能 + references 全量 vendored（9 个文本文件）；引擎不入库，install.sh 从锁定克隆 `uv pip install` 进 video-studio/.venv，**必须连带 rapidocr-onnxruntime**（缺它 OCR 字幕层静默禁用，2026-11-07 实测） |
| video-shotcraft（参考层） | github.com/Vincentwei1021/video-shotcraft | 1266a3ec4831289c4d893d42dd5102723658039a | Apache-2.0（已核实，非该作者另一仓的 PolyForm） | **不装技能**：仅 124 张 shots 配方卡 + sequences + sound-design/music-beat-sync/aesthetic-rules/jianying-export 文档摘录 vendored 在 skills/video-workflow/references/shotcraft/；其 Remotion 引擎/模板不装 |
| pyJianYingDraft | PyPI pyJianYingDraft==0.3.1 | — | Apache-2.0 | install.sh 装进 video-studio/.venv |
| faster-whisper | PyPI（钉 av<19） | — | MIT | 同上 |

2026-11-01 第二批评估的其余仓库（均不锁定、不安装）：anything2explainer、video-talkcraft（PolyForm 非商业 + Remotion 引擎，方法已吸收进总控「方法规范与参考层」）；motion-video-kit、motionmaxxing、huashu-motion、animate、openfilm（与现有引擎同层或落地形态不合，可取方法已吸收，理由见总控技能「不要做的事」）；FreeVideo（本地跑 MiniMax H3 的独立 app——用户 2026-11-01 决定不依赖本地 GPU，不采用，H3 原生规格只走云端通道）。

2026-11-06 第三批评估的其余项（均不锁定、不安装）：fy-code-animation（★238，github.com/Akillll-DuoHe/fy-code-animation——其 341 风格库本体不在仓库、自订许可禁止付费再打包、Remotion 落地、本地 ACE-Step 配乐需 GPU；只吸收方法三点进总控：词锚 rigor、音乐四案、气势词/字形轮廓）；skool.com/mromi「AI Creator Lab」（付费社群 $45/月，变现课程非工具，跳过）。

注意（已实测，见 skills/video-workflow/SKILL.md「已验证的环境事实」）：
- Playwright Chromium 在受限网络下用 npmmirror 直下 CFT 包手动安装，install.sh 已内置该方法。
- HyperFrames 渲染需 TMPDIR 指到大磁盘目录、HYPERFRAMES_BROWSER_PATH 指到 Playwright 无头 Chrome、GSAP 等 CDN 库本地化（jsdelivr 在目标网络不可用）。
- edge-tts 在 Muse 云 VM 被出口代理掐断，在 Windows 本机可用。

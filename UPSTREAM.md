# 上游锁定清单（2026-10-31 验证）

install.sh 按下表 commit 拉取/恢复。升级上游时先改这里、验证、再升本仓版本。

| 上游 | 仓库 | 锁定 commit | 许可 | 入库方式 |
|---|---|---|---|---|
| huashu-art-motion | github.com/alchaincyf/huashu-art-motion | 8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c | MIT（部分素材除外，见其仓库） | 不 vendored（74MB，含字体/图片二进制）；install.sh clone 后 checkout |
| anatomy | github.com/wheresryan22/anatomy | 1482e8469b0a9e0d8cc18ea2740a01423d29ae80 | MIT | 不 vendored（27MB，含图片）；install.sh clone 后 checkout |
| HyperFrames 技能 | github.com/heygen-com/hyperframes（skills/ 子目录） | a04b45a6db0d1f724be9cf1985c3b13657195f0d | Apache-2.0 | 文本部分 vendored 在 skills/ 下（已核对 SKILL.md 与该 commit 字节一致）；排除的二进制：hyperframes 的 6 个 .woff2 字体、media-use 的 19 个 .mp3 音效——install.sh 从上游补齐完整目录，覆盖 vendored 副本 |
| dataviz | github.com/JimLiu/baoyu-design（skills/dataviz） | 25f1c06c4d7c6619aa7c3ded96302c9e5f2ac847 | MIT | 全量 vendored（10 个文本文件） |
| MoneyPrinterTurbo | github.com/harry0703/MoneyPrinterTurbo | 8dbfbb8e9de1b8f9d745d73a8e9f07464248cdd9 | MIT | 不 vendored（独立应用）；install.sh clone 到 video-studio/apps 并装 venv |
| pyJianYingDraft | PyPI pyJianYingDraft==0.3.1 | — | Apache-2.0 | install.sh 装进 video-studio/.venv |
| faster-whisper | PyPI（钉 av<19） | — | MIT | 同上 |

注意（已实测，见 skills/video-workflow/SKILL.md「已验证的环境事实」）：
- Playwright Chromium 在受限网络下用 npmmirror 直下 CFT 包手动安装，install.sh 已内置该方法。
- HyperFrames 渲染需 TMPDIR 指到大磁盘目录、HYPERFRAMES_BROWSER_PATH 指到 Playwright 无头 Chrome、GSAP 等 CDN 库本地化（jsdelivr 在目标网络不可用）。
- edge-tts 在 Muse 云 VM 被出口代理掐断，在 Windows 本机可用。

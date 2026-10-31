# Changelog

## v1.0.0 — 2026-10-31

首个版本：调研选型 + 全路线实测打通后建仓。

- 总控技能 video-workflow（A–G 七条路线、通用管线、环境事实、禁区清单）
- vendored 技能：dataviz（全量）、HyperFrames 官方 4 技能（文本部分）
- studio 管线脚本：assemble.py / transcribe.py / make_jianying_draft.py
- install.sh 一键恢复（上游按 UPSTREAM.md 锁定 commit）
- 验证基线：huashu 片段渲染、HyperFrames 渲染、原生 TTS+字幕烧录成片、pyJianYingDraft 草稿、faster-whisper 转写、MoneyPrinterTurbo CLI 均实测通过；edge-tts 在云 VM 不可用（已注明）

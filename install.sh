#!/usr/bin/env bash
# video-workflow 一键恢复脚本（v1.0.0）
# 用法: bash install.sh        环境变量: WORKSPACE(默认 ~/workspace)
# 做的事: 1) 技能 -> $WORKSPACE/custom-skills  2) 管线 -> $WORKSPACE/video-studio
#         3) 上游技能按 UPSTREAM.md 锁定 commit 克隆  4) venv 依赖
#         5) Playwright Chromium(npmmirror 直装)  6) MoneyPrinterTurbo
set -euo pipefail
WS="${WORKSPACE:-$HOME/workspace}"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DST="$WS/custom-skills"
STUDIO="$WS/video-studio"
export PATH="$HOME/.local/bin:$PATH"

HUASHU_SHA=8a0d7d72ca65fcce6f8ba82c4a6c8dfe35b8422c
ANATOMY_SHA=1482e8469b0a9e0d8cc18ea2740a01423d29ae80
HF_SHA=a04b45a6db0d1f724be9cf1985c3b13657195f0d
MPT_SHA=8dbfbb8e9de1b8f9d745d73a8e9f07464248cdd9

mkdir -p "$SKILLS_DST" "$STUDIO"/{scripts,projects,output,apps,.tmp}

echo "== 1/6 vendored skills =="
cp -R "$REPO_DIR/skills/." "$SKILLS_DST/"

echo "== 2/6 studio scripts =="
cp "$REPO_DIR/studio/scripts/"*.py "$STUDIO/scripts/"
cp "$REPO_DIR/studio/README-视频工作流.md" "$STUDIO/" 2>/dev/null || true

clone_pinned() { # url sha dst
  if [ ! -d "$3/.git" ]; then git clone "$1" "$3"; fi
  git -C "$3" fetch --depth 1 origin "$2" 2>/dev/null || git -C "$3" fetch origin
  git -C "$3" checkout -q "$2"
}

echo "== 3/6 upstream skills (pinned) =="
TMPCLONE="$(mktemp -d)"
clone_pinned https://github.com/alchaincyf/huashu-art-motion.git "$HUASHU_SHA" "$TMPCLONE/huashu"
rsync -a --exclude='.git' "$TMPCLONE/huashu/" "$SKILLS_DST/huashu-art-motion/"
clone_pinned https://github.com/wheresryan22/anatomy.git "$ANATOMY_SHA" "$TMPCLONE/anatomy"
rsync -a --exclude='.git' "$TMPCLONE/anatomy/" "$SKILLS_DST/anatomy/"
clone_pinned https://github.com/heygen-com/hyperframes.git "$HF_SHA" "$TMPCLONE/hf"
for s in hyperframes hyperframes-cli hyperframes-registry media-use; do
  rsync -a "$TMPCLONE/hf/skills/$s/" "$SKILLS_DST/$s/"   # 覆盖 vendored 副本，补齐二进制资源
done
rm -rf "$TMPCLONE"

echo "== 4/6 python venv (pyJianYingDraft + faster-whisper + edge-tts) =="
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
[ -d "$STUDIO/.venv" ] || uv venv "$STUDIO/.venv" --python 3.12
uv pip install --python "$STUDIO/.venv/bin/python" pyJianYingDraft==0.3.1 faster-whisper "av<19" edge-tts pip-system-certs

echo "== 5/6 playwright chromium (npmmirror CFT 156) =="
if [ ! -x "$HOME/.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell" ]; then
  DL="$(mktemp -d)"; cd "$DL"
  for f in chrome-linux64 chrome-headless-shell-linux64; do
    curl -L -C - --retry 3 -o "$f.zip" "https://cdn.npmmirror.com/binaries/playwright/builds/cft/156.0.8078.4/linux64/$f.zip"
  done
  mkdir -p "$HOME/.cache/ms-playwright/chromium-1248" "$HOME/.cache/ms-playwright/chromium_headless_shell-1248"
  unzip -q chrome-linux64.zip && mv chrome-linux64 "$HOME/.cache/ms-playwright/chromium-1248/chrome-linux"
  unzip -q chrome-headless-shell-linux64.zip && mv chrome-headless-shell-linux64 "$HOME/.cache/ms-playwright/chromium_headless_shell-1248/"
  touch "$HOME/.cache/ms-playwright/chromium-1248/INSTALLATION_COMPLETE" "$HOME/.cache/ms-playwright/chromium_headless_shell-1248/INSTALLATION_COMPLETE"
  cd - >/dev/null; rm -rf "$DL"
fi

echo "== 6/6 MoneyPrinterTurbo (pinned; 首次真跑前需在 config.toml 填 LLM key + Pexels key) =="
clone_pinned https://github.com/harry0703/MoneyPrinterTurbo.git "$MPT_SHA" "$STUDIO/apps/MoneyPrinterTurbo"
cd "$STUDIO/apps/MoneyPrinterTurbo"
[ -d .venv ] || uv venv .venv --python 3.12
uv pip install --python .venv/bin/python --overrides requirements-security.txt -r requirements.txt

echo "完成。HyperFrames 渲染时记得:"
echo "  export TMPDIR=$STUDIO/.tmp"
echo "  export HYPERFRAMES_BROWSER_PATH=\$HOME/.cache/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell"
echo "  GSAP 等 CDN 库需本地化到项目 assets/（jsdelivr 在目标网络不可用）"

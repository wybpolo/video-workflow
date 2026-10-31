#!/usr/bin/env python3
"""用 faster-whisper 把音/视频转写成 SRT（词级时间戳可选）。
用法: .venv/bin/python scripts/transcribe.py <输入音视频> [--model base] [--language zh] [--out out.srt]
模型首次使用会从 HuggingFace 下载（tiny~75MB / base~145MB / small~466MB）。
"""
import argparse, os, sys

def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--model", default="base")
    ap.add_argument("--language", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    from faster_whisper import WhisperModel
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(a.input, language=a.language, vad_filter=True)
    out = a.out or (os.path.splitext(a.input)[0] + ".srt")
    with open(out, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n{fmt(seg.start)} --> {fmt(seg.end)}\n{seg.text.strip()}\n\n")
    print(f"language={info.language} -> {out}")

if __name__ == "__main__":
    main()

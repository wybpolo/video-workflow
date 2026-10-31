#!/usr/bin/env python3
"""拼接镜头片段 + 混口播/BGM + 可选烧字幕，输出成片。
用法:
  python3 scripts/assemble.py clip1.mp4 clip2.mp4 ... --out 成片.mp4
      [--voice 口播.wav] [--bgm 音乐.mp3] [--subs 字幕.srt] [--fps 30]
所有片段须同宽高同帧率（huashu/HyperFrames 管线默认满足）。
"""
import argparse, subprocess, os, sys, tempfile

def run(cmd):
    print("+", " ".join(cmd[:3]), "...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:]); sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice", default=None)
    ap.add_argument("--bgm", default=None)
    ap.add_argument("--subs", default=None)
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        lst = os.path.join(td, "list.txt")
        with open(lst, "w") as f:
            for c in a.clips:
                f.write(f"file '{os.path.abspath(c)}'\n")
        video = os.path.join(td, "video.mp4")
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
             "-r", str(a.fps), "-c:v", "libx264", "-crf", "16",
             "-pix_fmt", "yuv420p", "-an", video])

        inputs = ["-i", video]; filters = []; amix = []
        if a.voice:
            inputs += ["-i", a.voice]; amix.append("[1:a]loudnorm[a1]")
        if a.bgm:
            idx = 2 if a.voice else 1
            inputs += ["-i", a.bgm]
            amix.append(f"[{idx}:a]volume=0.12,aloop=loop=-1:duration=longest[a2]")
        cur = video
        if amix:
            fc = ";".join(amix)
            if len(amix) == 2:
                fc += ";[a1][a2]amix=inputs=2:duration=first[aout]"
                maps = ["-map", "0:v", "-map", "[aout]"]
            else:
                fc += ""  # single audio handled below
                maps = ["-map", "0:v", "-map", "[a1]" if a.voice else "[a2]"]
            mixed = os.path.join(td, "mixed.mp4")
            run(["ffmpeg", "-y", "-i", video] + inputs[2:] +
                ["-filter_complex", fc] + maps +
                ["-c:v", "copy", "-c:a", "aac", "-shortest", mixed])
            cur = mixed
        if a.subs:
            style = "FontName=Noto Sans CJK SC,FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,Outline=2,Alignment=2,MarginV=40"
            run(["ffmpeg", "-y", "-i", cur, "-vf",
                 f"subtitles={os.path.abspath(a.subs)}:force_style='{style}'",
                 "-c:a", "copy", a.out])
        else:
            run(["cp", cur, a.out])
    print("done ->", a.out)

if __name__ == "__main__":
    main()

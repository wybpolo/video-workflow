#!/usr/bin/env python3
"""Read-only full-decode technical video check; writes only the requested report."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def run(argv):
    return subprocess.run([str(x) for x in argv], capture_output=True, text=True, encoding='utf-8', errors='replace')


def verify(args):
    path = args.video.resolve()
    if not path.is_file() or not path.stat().st_size:
        raise ValueError('video missing or empty')
    fps = Fraction(args.fps)
    if fps <= 0 or args.frames <= 0:
        raise ValueError('fps and frames must be positive')
    width, height = map(int, args.size.lower().split('x'))
    probe = run([args.ffprobe, '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                 'stream=width,height,avg_frame_rate,r_frame_rate,nb_read_frames,duration,sample_aspect_ratio,pix_fmt:format=duration', '-of', 'json', path])
    if probe.returncode:
        raise ValueError('ffprobe failed: ' + probe.stderr[-3000:])
    data = json.loads(probe.stdout)
    if not data.get('streams'):
        raise ValueError('no video stream')
    stream = data['streams'][0]
    errors, warnings = [], []
    actual_frames = int(stream.get('nb_read_frames', -1))
    actual_fps = Fraction(stream.get('avg_frame_rate', '0'))
    if (stream.get('width'), stream.get('height')) != (width, height):
        errors.append('output dimensions differ from requested size')
    if abs(float(actual_fps-fps)) > 0.001:
        errors.append(f'average fps {actual_fps} != expected {fps}')
    if actual_frames != args.frames:
        errors.append(f'decoded frames {actual_frames} != expected {args.frames}')
    expected_duration = args.frames / float(fps)
    video_duration = stream.get('duration')
    if video_duration not in (None, 'N/A'):
        if abs(float(video_duration)-expected_duration) > 1 / float(fps) + 0.001:
            errors.append('video stream duration differs by more than one frame')
    else:
        warnings.append('video stream duration unavailable; using decoded frames and average fps')
    decode = run([args.ffmpeg, '-hide_banner', '-v', 'error', '-xerror', '-i', path, '-map', '0:v:0', '-f', 'null', '-'])
    if decode.returncode or decode.stderr.strip():
        errors.append('full decode reported an error: ' + decode.stderr[-3000:])
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            digest.update(chunk)
    return {"schema": "car-video.video-check.v1", "file": str(path), "bytes": path.stat().st_size,
            "sha256": digest.hexdigest(), "expected": {"fps": str(fps), "frames": args.frames, "width": width, "height": height, "duration_sec": expected_duration},
            "stream": stream, "container_duration_sec": data.get('format', {}).get('duration'),
            "full_video_decode_pass": decode.returncode == 0 and not decode.stderr.strip(),
            "technical_pass": not errors, "errors": errors, "warnings": warnings,
            "visual_review_performed": False, "audio_review_performed": False,
            "scope": "dimensions, average fps, decoded frame count, video duration and full video decode; not CFR proof, audio or visual approval"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('video', type=Path)
    p.add_argument('--ffmpeg', required=True)
    p.add_argument('--ffprobe', required=True)
    p.add_argument('--fps', required=True)
    p.add_argument('--frames', type=int, required=True)
    p.add_argument('--size', required=True, help='WIDTHxHEIGHT')
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    try:
        result = verify(args)
    except (OSError, ValueError, KeyError, ZeroDivisionError) as exc:
        result = {"technical_pass": False, "errors": [str(exc)], "visual_review_performed": False}
    if args.report:
        if args.report.resolve() == args.video.resolve():
            print('Refusing to overwrite input video with report', file=sys.stderr)
            return 2
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['technical_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())

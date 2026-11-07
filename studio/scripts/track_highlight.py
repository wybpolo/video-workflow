#!/usr/bin/env python3
"""bbox 动态追踪 + 高亮 + 局部放大（汽车工作流 J 路线追踪组）v2。

v2 整合 car-video-production 的跟踪纪律（2026-11-07）：
- 默认光流追踪（稀疏 PyrLK + 前后向误差检查 + RANSAC 局部相似变换），CSRT 保留为 --tracker csrt；
- 轨迹输出归一化 xywh（左上原点，注明参考画面），原始框与平滑框都保留；
- 丢失帧 status=lost：画面上隐藏框/标签/放大窗（不展示陈旧位置），JSON 里保留最后可靠框供诊断；
- 不跨丢失段插值；切镜后必须重新初始化（本脚本只处理单个连续镜头）。

模式时间轴（--phases）：box 框+标签 / highlight 框外压暗 / zoom 追踪区画中画放大。
用法:
  track_highlight.py in.mp4 -o out.mp4 --start 3.0 --bbox 187,1,952,542 \
      --label "拓野 T9 · 涉水" --phases box:3,highlight:2.5,zoom:2.5 \
      --track-json track.json --strip strip.jpg
--bbox 为起始帧像素坐标 x,y,w,h；加 --norm 时按 0-1000 归一化给。
"""
import argparse, json, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
LK = dict(winSize=(21, 21), maxLevel=3,
          criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
FEAT = dict(maxCorners=300, qualityLevel=0.01, minDistance=5, blockSize=7)


def seed_points(gray, box):
    x, y, w, h = [int(v) for v in box]
    mask = np.zeros(gray.shape, np.uint8)
    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    pts = cv2.goodFeaturesToTrack(gray, mask=mask, **FEAT)
    return pts


class FlowTracker:
    """PyrLK 光流 + 前后向检查 + RANSAC 相似变换（car-video-production 工作台同款思路）。"""

    def __init__(self, frame, box):
        self.box = tuple(float(v) for v in box)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.prev_gray = gray
        self.pts = seed_points(gray, box)
        self.status = "tracking" if self.pts is not None and len(self.pts) >= 8 else "lost"

    def update(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.status == "lost" or self.pts is None or len(self.pts) < 8:
            # 在最后可靠框内重新播种角点尝试重捕获（本帧仍按 lost 隐藏）
            pts = seed_points(gray, self.box)
            if pts is not None and len(pts) >= 8:
                self.pts, self.prev_gray = pts, gray
                self.status = "tracking"
                return self.box, "reacquired"
            self.prev_gray = gray
            return self.box, "lost"
        p1, st1, _ = cv2.calcOpticalFlowPyrLK(self.prev_gray, gray, self.pts, None, **LK)
        p0, st0, _ = cv2.calcOpticalFlowPyrLK(gray, self.prev_gray, p1, None, **LK)
        fb = np.linalg.norm((self.pts - p0).reshape(-1, 2), axis=1)
        good = (st1.reshape(-1) == 1) & (fb < 1.5)
        if good.sum() < 8:
            self.status = "lost"
            self.prev_gray = gray
            return self.box, "lost"
        src = self.pts[good].reshape(-1, 2).astype(np.float64)
        dst = p1[good].reshape(-1, 2).astype(np.float64)
        M, inliers = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=3.0)
        if M is None or inliers is None or inliers.sum() < 6:
            self.status = "lost"
            self.prev_gray = gray
            return self.box, "lost"
        x, y, w, h = self.box
        corners = np.array([[x, y], [x + w, y], [x, y + h], [x + w, y + h]], np.float64)
        tc = corners @ M[:, :2].T + M[:, 2]
        nx, ny = tc.min(axis=0)
        mx, my = tc.max(axis=0)
        if mx - nx < 12 or my - ny < 12:
            self.status = "lost"
            self.prev_gray = gray
            return self.box, "lost"
        self.box = (nx, ny, mx - nx, my - ny)
        self.pts = dst[inliers.reshape(-1) == 1].reshape(-1, 1, 2).astype(np.float32)
        # 角点耗减时在新框内补种
        if len(self.pts) < 40:
            extra = seed_points(gray, self.box)
            if extra is not None:
                self.pts = np.vstack([self.pts, extra]).astype(np.float32)
        self.prev_gray = gray
        return self.box, "tracking"


class CSRTracker:
    def __init__(self, frame, box):
        self.t = cv2.TrackerCSRT_create()
        self.t.init(frame, tuple(int(v) for v in box))
        self.box = tuple(float(v) for v in box)

    def update(self, frame):
        ok, new = self.t.update(frame)
        if not ok:
            return self.box, "lost"
        self.box = tuple(float(v) for v in new)
        return self.box, "tracking"


def parse_phases(s, fps):
    phases, acc = [], 0
    for part in s.split(","):
        mode, dur = part.split(":")
        n = int(round(float(dur) * fps))
        phases.append((mode.strip(), acc, acc + n))
        acc += n
    return phases, acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--bbox", required=True, help="x,y,w,h（起始帧像素）")
    ap.add_argument("--norm", action="store_true", help="bbox 为 0-1000 归一化坐标")
    ap.add_argument("--label", default="")
    ap.add_argument("--phases", default="box:3,highlight:2.5,zoom:2.5")
    ap.add_argument("--tracker", choices=["flow", "csrt"], default="flow")
    ap.add_argument("--mask", choices=["dark", "blue", "red"], default="dark",
                    help="highlight 段的框外处理：dark 压暗 / blue|red 半透明彩色遮罩")
    ap.add_argument("--mask-alpha", type=float, default=0.38, help="彩色遮罩不透明度")
    ap.add_argument("--track-json", default=None)
    ap.add_argument("--strip", default=None)
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.input)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    phases, total_frames = parse_phases(args.phases, fps)
    if args.duration:
        total_frames = min(total_frames, int(args.duration * fps))
    bb = [float(v) for v in args.bbox.split(",")]
    if args.norm:
        bb = [bb[0] / 1000 * W, bb[1] / 1000 * H, bb[2] / 1000 * W, bb[3] / 1000 * H]

    cap.set(cv2.CAP_PROP_POS_FRAMES, int(args.start * fps))
    ok, frame = cap.read()
    if not ok:
        sys.exit("cannot read start frame")
    tracker = FlowTracker(frame, bb) if args.tracker == "flow" else CSRTracker(frame, bb)

    font = ImageFont.truetype(FONT, max(20, W // 42))
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", args.output],
        stdin=subprocess.PIPE)

    def mode_at(i):
        for m, a, b in phases:
            if a <= i < b:
                return m
        return phases[-1][0]

    track, strip_frames = [], []
    smooth = None
    lost_n = 0
    for i in range(total_frames):
        if i > 0:
            ok, frame = cap.read()
            if not ok:
                break
            raw_box, status = tracker.update(frame)
        else:
            raw_box, status = tracker.box, tracker.status if hasattr(tracker, "status") else "tracking"
        if smooth is None:
            smooth = raw_box
        elif status in ("tracking", "reacquired"):
            smooth = tuple(0.6 * n + 0.4 * o for n, o in zip(raw_box, smooth))
        if status == "lost":
            lost_n += 1
        x, y, w, h = [int(v) for v in smooth]
        track.append({
            "f": i, "t": round(args.start + i / fps, 3), "status": status,
            "xywh_norm": [round(v, 5) for v in (raw_box[0] / W, raw_box[1] / H, raw_box[2] / W, raw_box[3] / H)],
            "xywh_px": [int(v) for v in raw_box],
            "draw_px": [x, y, w, h],
        })
        out = frame.copy()
        if status != "lost":  # 丢失即隐藏，不展示陈旧位置
            mode = mode_at(i)
            if mode == "highlight":
                mask = np.zeros((H, W), np.uint8)
                cv2.rectangle(mask, (x, y), (x + w, y + h), 1, -1)
                inside = mask[..., None] > 0
                if args.mask == "dark":
                    out = np.where(inside, out, (out * 0.45).astype(np.uint8))
                else:
                    color = np.zeros_like(out)
                    color[:] = (220, 110, 0) if args.mask == "blue" else (40, 40, 230)  # BGR
                    tinted = (out * (1 - args.mask_alpha) * 0.8 + color * args.mask_alpha).astype(np.uint8)
                    out = np.where(inside, out, tinted)
            cv2.rectangle(out, (x, y), (x + w, y + h), (0, 200, 255), 3)
            if mode == "zoom":
                cx0, cy0 = max(0, x), max(0, y)
                crop = frame[cy0:cy0 + h, cx0:cx0 + w]
                if crop.size:
                    zw = W // 3
                    zx, zy = W - zw - 24, 24
                    zh = min(int(zw * crop.shape[0] / crop.shape[1]), H - zy)
                    zoomed = cv2.resize(crop, (zw, zh), interpolation=cv2.INTER_CUBIC)
                    out[zy:zy + zh, zx:zx + zw] = zoomed
                    cv2.rectangle(out, (zx, zy), (zx + zw, zy + zh), (0, 200, 255), 3)
            if args.label:
                pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
                d = ImageDraw.Draw(pil)
                tw = d.textlength(args.label, font=font)
                lx, ly = x, max(0, y - int(font.size * 1.5))
                d.rectangle([lx, ly, lx + tw + 20, ly + font.size + 14], fill=(0, 160, 200))
                d.text((lx + 10, ly + 6), args.label, font=font, fill=(255, 255, 255))
                out = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        proc.stdin.write(out.tobytes())
        if i % max(1, total_frames // 6) == 0:
            strip_frames.append(cv2.resize(out, (W // 3, H // 3)))
    proc.stdin.close()
    proc.wait()
    cap.release()

    if args.track_json:
        json.dump({"schema": "car-track.v2", "source": args.input, "start": args.start,
                   "fps": fps, "reference": {"width": W, "height": H},
                   "tracker": args.tracker, "init_bbox_px": [int(v) for v in bb],
                   "label": args.label, "lost_frames": lost_n,
                   "note": "xywh_norm 为左上原点归一化（参考 source 画面）；lost 帧 draw 已隐藏，xywh 保留最后可靠框供诊断，不可用于合成",
                   "frames": track},
                  open(args.track_json, "w"), ensure_ascii=False, indent=1)
    if args.strip and strip_frames:
        cv2.imwrite(args.strip, np.hstack(strip_frames[:6]))
    print(f"done: {len(track)} frames, lost={lost_n}, tracker={args.tracker} -> {args.output}")


if __name__ == "__main__":
    main()

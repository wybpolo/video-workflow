#!/usr/bin/env python3
"""按 JSON 规格生成剪映可编辑草稿（pyJianYingDraft 0.3.1 已验证 API）。
用法: .venv/bin/python scripts/make_jianying_draft.py spec.json <草稿父目录(必须已存在)>
spec.json 示例:
{
  "name": "我的草稿", "width": 1080, "height": 1920,
  "videos": [{"path": "a.mp4", "start": 0, "duration": 5}],
  "audios": [{"path": "voice.mp3", "start": 0}],
  "texts":  [{"text": "标题", "start": 0, "duration": 3, "size": 12}]
}
start/duration 单位秒。生成的草稿文件夹拷到 Windows 剪映草稿目录即可打开继续编辑。
注意: 自动导出仅剪映<=6.x 支持；本脚本只生成草稿。国际版 CapCut 不支持。
"""
import json, os, sys
import pyJianYingDraft as jy

US = 1_000_000

def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    parent = os.path.abspath(sys.argv[2])
    assert os.path.isdir(parent), f"草稿父目录必须已存在: {parent}"
    folder = jy.DraftFolder(parent)
    s = folder.create_draft(spec["name"], spec.get("width", 1080),
                            spec.get("height", 1920), allow_replace=True)
    if spec.get("videos"):
        ref = s.append_track(jy.TrackSpec(jy.TrackType.video))
        for v in spec["videos"]:
            mat = jy.VideoMaterial(v["path"])
            dur = int(v.get("duration", mat.duration / US) * US)
            seg = jy.VideoSegment(mat, jy.Timerange(int(v.get("start", 0) * US), dur))
            s.add_segment(seg, ref)
    if spec.get("audios"):
        ref = s.append_track(jy.TrackSpec(jy.TrackType.audio))
        for au in spec["audios"]:
            mat = jy.AudioMaterial(au["path"])
            dur = int(au.get("duration", mat.duration / US) * US)
            seg = jy.AudioSegment(mat, jy.Timerange(int(au.get("start", 0) * US), dur))
            s.add_segment(seg, ref)
    if spec.get("texts"):
        ref = s.append_track(jy.TrackSpec(jy.TrackType.text))
        for t in spec["texts"]:
            seg = jy.TextSegment(t["text"],
                                 jy.Timerange(int(t.get("start", 0) * US),
                                              int(t.get("duration", 3) * US)),
                                 style=jy.TextStyle(size=t.get("size", 10.0),
                                                    color=(1, 1, 1)))
            s.add_segment(seg, ref)
    s.save()
    out = os.path.join(parent, spec["name"], "draft_content.json")
    print("draft ->", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    main()

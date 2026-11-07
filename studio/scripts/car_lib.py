#!/usr/bin/env python3
"""汽车视频镜头/手法卡库（J 路线 RAG 拆视频层）：结构化检索版。

卡片两种：
  technique —— 手法卡（来自《拍车叙事手法》《卡车拍摄叙事》两份文档的 33 条沉淀 + 后续新增）
  shot      —— 镜头卡（rea-video 拆解参考片/成片的 breakdown.json 入库：镜号/时段/制作方式/置信度/OCR）
检索方式：字段加权关键词打分（title/tags 高权重），不是向量检索——胜在零依赖、可解释；
规划新片时先 search 拿相关手法卡与相似镜头卡，再套 J 路线证据链公式。

用法:
  car_lib.py stats
  car_lib.py ingest <breakdown.json> --name 片名 [--file 原片名]
  car_lib.py search "涉水 对比 高亮" [--kind shot|technique] [--top 8]
  car_lib.py add <card.json>          # 单张卡（JSON 对象）入库
库位置：~/workspace/video-studio/car-library/cards.jsonl（可用 CAR_LIB 环境变量改）
"""
import argparse, json, os, re, sys

LIB = os.environ.get("CAR_LIB", os.path.expanduser("~/workspace/video-studio/car-library/cards.jsonl"))


def load():
    if not os.path.exists(LIB):
        return []
    return [json.loads(l) for l in open(LIB, encoding="utf-8") if l.strip()]


def save(cards):
    os.makedirs(os.path.dirname(LIB), exist_ok=True)
    with open(LIB, "w", encoding="utf-8") as f:
        for c in cards:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")


def tokens(s):
    s = (s or "").lower()
    toks = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]{2,}", s)
    # 中文长串再切 2-gram，保证「涉水通过」能命中「涉水」
    grams = set()
    for t in toks:
        grams.add(t)
        if len(t) > 2 and re.fullmatch(r"[\u4e00-\u9fff]+", t):
            for i in range(len(t) - 1):
                grams.add(t[i:i + 2])
    return grams


def score(card, qtoks):
    fields = [(card.get("title", ""), 3), (" ".join(card.get("tags", [])), 3),
              (card.get("scene", ""), 1), (card.get("method", ""), 1),
              (card.get("function", ""), 1), (card.get("text", ""), 1),
              (card.get("category", ""), 2), (card.get("note", ""), 1)]
    sc = 0
    for text, w in fields:
        ct = tokens(text)
        sc += w * len(qtoks & ct)
    return sc


def cmd_search(a):
    cards = load()
    q = tokens(a.query)
    ranked = []
    for c in cards:
        if a.kind and c.get("kind") != a.kind:
            continue
        s = score(c, q)
        if s > 0:
            ranked.append((s, c))
    ranked.sort(key=lambda x: -x[0])
    for s, c in ranked[:a.top]:
        head = f"[{c.get('kind')}] {c.get('title', '')}"
        if c.get("kind") == "shot":
            head += f" · {c.get('start', '?')}–{c.get('end', '?')}s · {c.get('category', '')} · 置信 {c.get('confidence', '?')}"
        print(f"{head}  (score {s})")
        for k in ("scene", "method", "function", "source", "text"):
            if c.get(k):
                print(f"    {k}: {c[k]}")
    if not ranked:
        print("无命中。换关键词，或先 ingest 更多拆解。")


def cmd_ingest(a):
    d = json.load(open(a.breakdown, encoding="utf-8"))
    cards = load()
    have = {c.get("id") for c in cards}
    n = 0
    for s in d.get("shots", []):
        idx = s.get("index", n + 1)
        cid = f"shot:{a.name}#{idx}"
        if cid in have:
            continue
        base = s.get("base") or {}
        cat = base.get("label_zh") or s.get("verdict", "")
        conf = base.get("confidence", "")
        framing = ((s.get("aspects") or {}).get("framing") or {}).get("measured") or {}
        repl = (s.get("replication") or {}).get("route") or []
        tracks = ((s.get("text") or {}).get("tracks")) or []
        ocr = " ".join(t.get("text", "") for t in tracks if isinstance(t, dict))
        cards.append({
            "id": cid, "kind": "shot", "title": f"{a.name} · 镜{idx}",
            "tags": [a.name] + ([a.file] if a.file else []) + ([framing.get("shot_size")] if framing.get("shot_size") else []),
            "start": s.get("start"), "end": s.get("end"), "duration": s.get("duration"),
            "category": cat, "confidence": conf,
            "text": ocr,
            "note": ("复刻路线: " + " → ".join(repl)) if repl else "",
            "source": f"rea-video breakdown: {a.breakdown}",
            "retrieval_backend": "local-scan",
            "review_status": "needs_visual_review",
        })
        n += 1
    save(cards)
    print(f"ingested {n} shot cards from {a.name} (total {len(cards)})")


def cmd_add(a):
    card = json.load(open(a.card, encoding="utf-8"))
    cards = load()
    cards.append(card)
    save(cards)
    print(f"added: {card.get('id') or card.get('title')} (total {len(cards)})")


def cmd_stats(a):
    cards = load()
    from collections import Counter
    print("total:", len(cards), Counter(c.get("kind") for c in cards))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("--kind"); p.add_argument("--top", type=int, default=8); p.set_defaults(f=cmd_search)
    p = sub.add_parser("ingest"); p.add_argument("breakdown"); p.add_argument("--name", required=True); p.add_argument("--file"); p.set_defaults(f=cmd_ingest)
    p = sub.add_parser("add"); p.add_argument("card"); p.set_defaults(f=cmd_add)
    p = sub.add_parser("stats"); p.set_defaults(f=cmd_stats)
    a = ap.parse_args()
    a.f(a)

#!/usr/bin/env python3
"""把场景运行时记录的字幕时间轴（videos/out/<id>.cues.json）转成 WebVTT；--manifest 汇总时长与体积。

  python3 cues2vtt.py out/01-enumeration.cues.json ../site/public/videos/01-enumeration.vtt
  python3 cues2vtt.py --manifest out ../site/public/videos/manifest.json
"""
import json, os, sys
from pathlib import Path


def ts(t: float) -> str:
    h, r = divmod(max(t, 0.0), 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


def to_vtt(src: Path, dst: Path):
    d = json.loads(src.read_text(encoding="utf-8"))
    lines = ["WEBVTT", "", f"NOTE {d['title']} · USBTree（https://usbtree.gumuhub.com）", ""]
    for i, c in enumerate(d["cues"], 1):
        end = c["end"] if c["end"] is not None else d["duration"]
        if end - c["start"] < 0.3:
            continue
        lines += [str(i), f"{ts(c['start'])} --> {ts(end)}", c["text"], ""]
    dst.write_text("\n".join(lines), encoding="utf-8")


def manifest(outdir: Path, dst: Path):
    pub = dst.parent
    old = json.loads(dst.read_text(encoding="utf-8")) if dst.exists() else {}
    for f in sorted(outdir.glob("*.cues.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        mp4 = pub / f"{d['slug']}.mp4"
        if mp4.exists():
            old[d["slug"]] = {"title": d["title"], "duration": round(d["duration"], 1), "mp4_bytes": mp4.stat().st_size}
    dst.write_text(json.dumps(dict(sorted(old.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "--manifest":
        manifest(Path(sys.argv[2]), Path(sys.argv[3]))
    else:
        to_vtt(Path(sys.argv[1]), Path(sys.argv[2]))

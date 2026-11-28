#!/usr/bin/env bash
# 渲染 USBTree 代码视频 → site/public/videos/<id>.{mp4,png,vtt}（入库）
#
#   videos/render.sh            # 全部渲染（1080p30）
#   videos/render.sh 03-transfers 05-typec-pd   # 只渲染指定 id
#   QUALITY=draft videos/render.sh 01-enumeration   # 480p15 快速预览（只输出到 videos/out/，不覆盖站点文件）
#   WEBM=1 videos/render.sh     # 额外输出 VP9 WebM（默认不生成）
#
# 依赖：Python 3.10+、manim（pip install -r videos/requirements.txt）、ffmpeg、
#       字体 Noto Sans CJK SC（fonts-noto-cjk）与 JetBrains Mono（缺失时自动回退到其它等宽字体）。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
OUT="$HERE/out"                       # 中间产物（gitignore）
DEST="$ROOT/site/public/videos"       # 站点发布文件（入库）
MANIM="${MANIM:-manim}"
QUALITY="${QUALITY:-final}"
CRF="${CRF:-30}"
mkdir -p "$OUT" "$DEST"
export USBTREE_VIDEO_OUT="$OUT"

mapfile -t ROWS < <(python3 - "$HERE/videos.yaml" "$@" <<'PY'
import sys, re
text = open(sys.argv[1], encoding="utf-8").read()
want = set(sys.argv[2:])
for blk in re.split(r"\n  - ", text)[1:]:
    g = lambda k: (re.search(rf"^\s*{k}:\s*(.+)$", blk, re.M) or [None, ""])[1].strip()
    vid = blk.split("\n")[0].split(":", 1)[1].strip()
    if not want or vid in want:
        print("\t".join([vid, g("scene"), g("class"), g("poster")]))
PY
)
[ ${#ROWS[@]} -gt 0 ] || { echo "没有匹配的视频 id"; exit 1; }

for row in "${ROWS[@]}"; do
  IFS=$'\t' read -r ID SCENE CLASS POSTER <<<"$row"
  echo "▶ $ID ($CLASS)"
  if [ "$QUALITY" = draft ]; then
    "$MANIM" -ql --disable_caching --media_dir "$OUT/media/$ID" -o "$ID" "$HERE/scenes/$SCENE" "$CLASS"
    find "$OUT/media/$ID" -name "$ID.mp4" -exec cp {} "$OUT/$ID.draft.mp4" \;
    echo "  草稿：$OUT/$ID.draft.mp4"; continue
  fi
  "$MANIM" --resolution 1920,1080 --frame_rate 30 --disable_caching --media_dir "$OUT/media/$ID" -o "$ID" "$HERE/scenes/$SCENE" "$CLASS"
  SRC="$(find "$OUT/media/$ID/videos" -path "*1080p30*" -name "$ID.mp4" | head -1)"
  # H.264（静态矢量画面：tune animation + 较高 CRF 即可保持清晰，体积约 2–5 MB）
  ffmpeg -v error -y -i "$SRC" -c:v libx264 -preset slow -tune animation -crf "$CRF" -pix_fmt yuv420p \
    -movflags +faststart -an "$DEST/$ID.mp4"
  if [ "${WEBM:-0}" = 1 ]; then
    ffmpeg -v error -y -i "$SRC" -c:v libvpx-vp9 -b:v 0 -crf 42 -row-mt 1 -deadline good -an "$DEST/$ID.webm"
  fi
  # 封面：1280×720 PNG（调色板量化，矢量画面几乎无损，约 100 KB）
  ffmpeg -v error -y -ss "$POSTER" -i "$SRC" -frames:v 1 \
    -vf "scale=1280:-2:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=single[p];[b][p]paletteuse=dither=none" "$DEST/$ID.png"
  ffmpeg -v error -y -ss "$POSTER" -i "$SRC" -frames:v 1 -vf scale=640:-2 -q:v 4 "$DEST/$ID.thumb.jpg"   # 首页卡片缩略图
  # 字幕：场景运行时记录的时间轴 → WebVTT
  python3 "$HERE/cues2vtt.py" "$OUT/$ID.cues.json" "$DEST/$ID.vtt"
  ls -lh "$DEST/$ID".* | awk '{print "  " $5 "\t" $9}'
done
python3 "$HERE/cues2vtt.py" --manifest "$OUT" "$DEST/manifest.json"
echo "完成 → $DEST"

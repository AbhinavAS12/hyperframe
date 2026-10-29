#!/bin/bash
# Stabilize one shot from a 4K vertical original into a 1080x1920 clip for the reel.
#
# usage: tools/stabilize.sh SRC START DUR OUT [FPS=30] [SMOOTH=15] [MARGIN=1.10] [MAXSHIFT=40] [MAXANGLE=0.012]
#
# Why clamped: vidstab's automatic zoom (optzoom) sizes one fixed zoom big enough to hide the borders
# during the camera operator's deliberate moves, which over-cropped this footage by up to 2.2x.
# Instead the source is scaled to MARGIN x 1080x1920, corrections are clamped (MAXSHIFT px, MAXANGLE rad)
# to what that margin hides, and the result is center-cropped back to 1080x1920. Shake is removed;
# deliberate camera moves are left alone.
set -euo pipefail
SRC=$1; ST=$2; DU=$3; OUT=$4
FPS=${5:-30}; SM=${6:-15}; MARGIN=${7:-1.10}; MS=${8:-40}; MA=${9:-0.012}
W=$(python3 -c "print(int(round(1080*$MARGIN/2))*2)")
H=$(python3 -c "print(int(round(1920*$MARGIN/2))*2)")
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
ffmpeg -v error -y -ss "$ST" -i "$SRC" -t "$DU" -an \
  -vf "scale=$W:$H:force_original_aspect_ratio=increase:flags=lanczos,crop=$W:$H,fps=$FPS" \
  -c:v libx264 -crf 10 -preset ultrafast "$TMP/mid.mp4"
ffmpeg -v error -y -i "$TMP/mid.mp4" \
  -vf "vidstabdetect=shakiness=5:accuracy=15:stepsize=6:result=$TMP/t.trf" -f null -
ffmpeg -v error -y -i "$TMP/mid.mp4" \
  -vf "vidstabtransform=input=$TMP/t.trf:smoothing=$SM:maxshift=$MS:maxangle=$MA:optzoom=0:zoom=0:crop=black:interpol=bicubic,crop=1080:1920,unsharp=3:3:0.35" \
  -c:v libx264 -crf 19 -preset medium -g 15 -pix_fmt yuv420p -movflags +faststart "$OUT"

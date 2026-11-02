#!/usr/bin/env python3
"""Export the edit for Premiere Pro / DaVinci Resolve (FCP7 XML) and CapCut (numbered clips).

usage: python3 tools/export_nle.py [--footage DIR] [--handles 2.0]

Writes export/MDX_Reel_Kit/:
  media/<scene>-<id>.mp4            stabilized 1080x1920 shots with HANDLES s of extra footage each side
  media/title-overlay.mov           the title card, ProRes 4444 with alpha
  media/allegiance-outro.mp4, media/music.wav, media/reference-render.mp4
  MDX_Reel_Premiere.xml             timeline on the stabilized shots (V1 shots + outro, V2 title, V3 reference off)
  MDX_Reel_Premiere_4K_originals.xml  same cut on the untouched 4K originals (whole clips, relink to your files)
  CapCut/NN_<scene>-<id>.mp4        every shot trimmed to its exact length, in timeline order
"""
import argparse, os, shutil, subprocess, sys
from urllib.parse import quote
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_reel as br  # noqa: E402

ROOT = br.ROOT
# names of the originals as they appear in the Drive folder
DRIVE_NAMES = {f["name"]: f["drive_title"] for f in __import__("json").load(open(os.path.join(br.ROOT, "footage", "manifest.json")))["files"]}
FPS = 30


def fr(t):
    return int(round(t * FPS))


def probe(path, entry="format=duration"):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", entry, "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip().split("\n")[0]
    return out


def file_el(fid, name, rel, dur_frames, width, height, rate=FPS, audio=False, video=True):
    return f"""<file id="{fid}"><name>{escape(name)}</name><pathurl>{escape(quote(rel))}</pathurl>
<rate><timebase>{rate}</timebase><ntsc>FALSE</ntsc></rate><duration>{dur_frames}</duration>
<media>{f'<video><samplecharacteristics><width>{width}</width><height>{height}</height></samplecharacteristics></video>' if video else ''}{'<audio><channelcount>2</channelcount></audio>' if audio else ''}</media></file>"""


def clip_el(cid, name, start, end, in_f, out_f, file_xml, rate=FPS, scale=None, enabled=True):
    motion = ""
    if scale is not None:
        motion = f"""<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory>
<effecttype>motion</effecttype><mediatype>video</mediatype>
<parameter><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax><value>{scale}</value></parameter>
</effect></filter>"""
    return f"""<clipitem id="{cid}"><name>{escape(name)}</name><enabled>{'TRUE' if enabled else 'FALSE'}</enabled>
<rate><timebase>{rate}</timebase><ntsc>FALSE</ntsc></rate><start>{start}</start><end>{end}</end><in>{in_f}</in><out>{out_f}</out>
{file_xml}{motion}</clipitem>"""


def sequence_xml(name, dur, v_tracks, a_tracks):
    vt = "".join(f"<track>{''.join(t)}</track>" for t in v_tracks)
    at = "".join(f"<track>{''.join(t)}</track>" for t in a_tracks)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4"><sequence id="seq1"><name>{escape(name)}</name><duration>{dur}</duration>
<rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>
<media><video><format><samplecharacteristics><rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>
<width>1080</width><height>1920</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>{vt}</video>
<audio>{at}</audio></media></sequence></xmeml>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--footage", default=os.environ.get("FOOTAGE_DIR", os.path.join(ROOT, "footage")))
    ap.add_argument("--handles", type=float, default=2.0)
    args = ap.parse_args()
    edit = br.load_edit()
    clk, scenes = br.plan(edit)
    kit = os.path.join(ROOT, "export", "MDX_Reel_Kit")
    media = os.path.join(kit, "media")
    capcut = os.path.join(kit, "CapCut")
    os.makedirs(media, exist_ok=True)
    os.makedirs(capcut, exist_ok=True)
    total = fr(edit["duration_s"])

    shots = [(sc, sh) for sc in scenes for sh in sc["shots_resolved"]]
    v1, v1_4k, files_seen = [], [], {}
    n = 0
    for k, (sc, sh) in enumerate(shots, 1):
        name = f"{sc['id']}-{sh['id']}"
        src = os.path.join(args.footage, f"{sh['clip']}.MP4")
        a = max(0.0, sh["in_s"] - args.handles)
        src_dur = float(probe(src))
        b = min(src_dur, sh["in_s"] + (sh["abs_end"] - sh["abs_start"]) * sh.get("rate", 1.0) + args.handles)
        out = os.path.join(media, f"{name}.mp4")
        if not os.path.exists(out):
            st = sh.get("stab", {})
            print(f"stabilize {name} ({sh['clip']} {a:.2f}-{b:.2f})", flush=True)
            subprocess.run([os.path.join(ROOT, "tools", "stabilize.sh"), src, f"{a:.3f}", f"{b - a:.3f}", out, "30",
                            str(st.get("smooth", 15)), str(st.get("margin", 1.10)), str(st.get("maxshift", 40)),
                            str(st.get("maxangle", 0.012))], check=True)
        start, end = fr(sh["abs_start"]), fr(sh["abs_end"])
        in_f = fr(sh["in_s"] - a)
        dur_f = fr(float(probe(out)))
        fid = f"file-{name}"
        v1.append(clip_el(f"clip-{name}", f"{k:02d} {name} ({sh['clip']}) {sh.get('note', '')}", start, end,
                          in_f, in_f + (end - start), file_el(fid, f"{name}.mp4", f"media/{name}.mp4", dur_f, 1080, 1920)))
        # the same cut on the untouched 4K original (50 fps source, whole clip available)
        ofid = f"orig-{sh['clip']}"
        oname = DRIVE_NAMES.get(sh["clip"], f"{sh['clip']}.MP4")
        oxml = f'<file id="{ofid}"/>' if ofid in files_seen else file_el(
            ofid, oname, oname, int(round(src_dur * 50)), 2160, 3840, rate=50, audio=True)
        files_seen[ofid] = True
        oin = int(round(sh["in_s"] * 50))
        v1_4k.append(clip_el(f"o-{name}", f"{k:02d} {name} ({sh['clip']})", start, end, oin,
                             oin + int(round((end - start) / FPS * 50)), oxml, rate=50, scale=50))
        # CapCut: exact-length piece, in order
        cap = os.path.join(capcut, f"{k:02d}_{name}.mp4")
        if not os.path.exists(cap):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sh['in_s'] - a:.3f}", "-i", out, "-t",
                            f"{(end - start) / FPS:.3f}", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                            "-pix_fmt", "yuv420p", "-an", cap], check=True)
        n = k

    # outro, music, reference render, title overlay
    o = edit["outro"]
    shutil.copy(os.path.join(ROOT, o["src"]), os.path.join(media, "allegiance-outro.mp4"))
    shutil.copy(os.path.join(ROOT, o["src"]), os.path.join(capcut, f"{n + 1:02d}_allegiance-outro.mp4"))
    o_start = fr(clk.t(o["start_beat"]))
    o_len = fr(float(probe(os.path.join(media, "allegiance-outro.mp4"))))
    outro_xml = clip_el("clip-outro", "Allegiance outro", o_start, total, 0, total - o_start,
                        file_el("file-outro", "allegiance-outro.mp4", "media/allegiance-outro.mp4", o_len, 1080, 1920))
    music_src = os.path.join(ROOT, edit["music"][0]["src"])
    shutil.copy(music_src, os.path.join(media, "music.wav"))
    m_len = fr(float(probe(music_src)))
    a1 = []
    for i, m in enumerate(edit["music"]):
        ms = fr(clk.t(m["start_beat"]))
        me = fr(clk.t(m["end_beat"])) if "end_beat" in m else fr(m["end_s"])
        mi = fr(m["media_start_s"])
        fxml = file_el("file-music", "music.wav", "media/music.wav", m_len, 0, 0, audio=True, video=False) if i == 0 \
            else '<file id="file-music"/>'
        a1.append(f"""<clipitem id="music-{i}"><name>music {i + 1}</name><rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>
<start>{ms}</start><end>{me}</end><in>{mi}</in><out>{mi + me - ms}</out>{fxml}<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>""")
    ref = os.path.join(media, "reference-render.mp4")
    renders = sorted(f for f in os.listdir(os.path.join(ROOT, "renders")) if f.startswith("mdx-career-expo-v"))
    shutil.copy(os.path.join(ROOT, "renders", renders[-1]), ref)
    ref_xml = clip_el("clip-ref", "reference render (finished cut, enable to compare)", 0, total, 0, total,
                      file_el("file-ref", "reference-render.mp4", "media/reference-render.mp4", total, 1080, 1920, audio=True),
                      enabled=False)
    t = edit["title"]
    t_start, t_end = fr(clk.t(t["start_beat"])), fr(clk.t(t["end_beat"]))
    title_xml = clip_el("clip-title", "Title card (transparent)", t_start, t_end, 0, t_end - t_start,
                        file_el("file-title", "title-overlay.mov", "media/title-overlay.mov", t_end - t_start, 1080, 1920))
    shutil.copy(os.path.join(media, "title-overlay.mov"), os.path.join(capcut, "title-overlay.mov")) \
        if os.path.exists(os.path.join(media, "title-overlay.mov")) else None
    shutil.copy(os.path.join(media, "music.wav"), os.path.join(capcut, "music.wav"))

    with open(os.path.join(kit, "MDX_Reel_Premiere.xml"), "w") as f:
        f.write(sequence_xml("MDX Reel - stabilized shots", total, [v1 + [outro_xml], [title_xml], [ref_xml]], [a1]))
    with open(os.path.join(kit, "MDX_Reel_Premiere_4K_originals.xml"), "w") as f:
        f.write(sequence_xml("MDX Reel - 4K originals", total, [v1_4k + [outro_xml], [title_xml]], [a1]))
    print(f"exported {n} shots to {kit}")


if __name__ == "__main__":
    main()

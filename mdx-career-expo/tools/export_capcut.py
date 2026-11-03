#!/usr/bin/env python3
"""Export the reel as an editable CapCut desktop project (draft), built from edit.json.

usage: python3 tools/export_capcut.py --media DIR --out DIR [--media-root "C:/MDX_Reel_CapCut/media"]

--media holds the WHOLE stabilized source clips (<CLIP>.mp4, 1080x1920), the title overlay (title-overlay.mov),
the outro and the music. Every shot on the timeline is a trim of a whole clip, so in CapCut you can drag its
edges or slide it to pick another moment. Kept from the HyperFrames cut: beat-timed cuts, slow motion, the
15-frame optical zoom and the slow pushes (scale keyframes), the white flash at the booth, the logo's
blur-to-focus (CapCut "Focus" intro), the title overlay, the music edit and the outro.
The radial blur on the three walking shots is baked into their own *_look.mp4 clips.
Material paths are rewritten to --media-root, where the person keeps the media folder.
"""
import argparse, json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_reel as br  # noqa: E402
import pycapcut as cc  # noqa: E402

US = 1_000_000


def us(t):
    return int(round(t * US))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--media", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="MDX_Reel")
    ap.add_argument("--media-root", default="C:/MDX_Reel_CapCut/media")
    args = ap.parse_args()
    edit = br.load_edit()
    clk, scenes = br.plan(edit)
    media = os.path.abspath(args.media)

    # copy the non-footage media next to the clips
    shutil.copy(os.path.join(br.ROOT, edit["outro"]["src"]), os.path.join(media, "allegiance-outro.mp4"))
    shutil.copy(os.path.join(br.ROOT, edit["music"][0]["src"]), os.path.join(media, "music.wav"))

    os.makedirs(args.out, exist_ok=True)
    folder = cc.DraftFolder(args.out)
    script = folder.create_draft(args.name, 1080, 1920, fps=edit.get("fps", 30), allow_replace=True)
    script.add_track(cc.TrackType.video, "main")                           # main track: shots + outro
    script.add_track(cc.TrackType.video, "title", relative_index=1)        # title overlay
    script.add_track(cc.TrackType.audio)

    oz = edit.get("optical_zoom", {})
    oz_dur, oz_scale = oz.get("frames", 15) / clk.fps, oz.get("scale", 1.08)
    materials = {}
    segs = []
    for sc in scenes:
        for sh in sc["shots_resolved"]:
            clip = sh["clip"]
            path = os.path.join(media, f"{clip}.mp4")
            if sh.get("radial_blur"):
                look = os.path.join(media, f"{clip}_look.mp4")
                if not os.path.exists(look):
                    print(f"bake radial blur into {os.path.basename(look)}", flush=True)
                    br.prebake({"radial_blur": sh["radial_blur"]}, path, look)
                path = look
            mat = materials.setdefault(path, cc.VideoMaterial(path))
            start, dur = sh["abs_start"], sh["abs_end"] - sh["abs_start"]
            rate = sh.get("rate", 1.0)
            seg = cc.VideoSegment(mat, cc.Timerange(us(start), us(dur)),
                                  source_timerange=cc.Timerange(us(sh["in_s"]), us(dur * rate)), speed=rate)
            # optical zoom on every shot, the slow push on top where the cut has one
            push = sh.get("move", {}).get("to", 1.0)
            if not sh.get("no_zoom"):
                seg.add_keyframe(cc.KeyframeProperty.uniform_scale, 0, 1.0)
                seg.add_keyframe(cc.KeyframeProperty.uniform_scale, us(oz_dur), oz_scale)
                if push != 1.0:
                    seg.add_keyframe(cc.KeyframeProperty.uniform_scale, us(dur) - 1, oz_scale * push)
            elif push != 1.0:
                seg.add_keyframe(cc.KeyframeProperty.uniform_scale, 0, 1.0)
                seg.add_keyframe(cc.KeyframeProperty.uniform_scale, us(dur) - 1, push)
            if sh.get("blur_in"):
                seg.add_animation(cc.IntroType.Focus, duration=us(sh["blur_in"]))
            segs.append((sh, seg))
    # the flash into the booth: CapCut transitions sit on the segment BEFORE the cut
    for i, (sh, seg) in enumerate(segs[1:], 1):
        if (sh.get("enter") or "") == "flash":
            segs[i - 1][1].add_transition(cc.TransitionType.White_Flash, duration=us(0.3))
    for _, seg in segs:
        script.add_segment(seg, "main")

    o = edit["outro"]
    o_start = clk.t(o["start_beat"])
    outro = cc.VideoMaterial(os.path.join(media, "allegiance-outro.mp4"))
    script.add_segment(cc.VideoSegment(outro, cc.Timerange(us(o_start), us(edit["duration_s"] - o_start)),
                                       source_timerange=cc.Timerange(0, us(edit["duration_s"] - o_start))), "main")

    t = edit["title"]
    ts, te = clk.t(t["start_beat"]), clk.t(t["end_beat"])
    title = cc.VideoMaterial(os.path.join(media, "title-overlay.mov"))
    script.add_segment(cc.VideoSegment(title, cc.Timerange(us(ts), us(te - ts))), "title")

    music = cc.AudioMaterial(os.path.join(media, "music.wav"))
    for m in edit["music"]:
        ms = clk.t(m["start_beat"])
        me = clk.t(m["end_beat"]) if "end_beat" in m else m["end_s"]
        script.add_segment(cc.AudioSegment(music, cc.Timerange(us(ms), us(me - ms)),
                                           source_timerange=cc.Timerange(us(m["media_start_s"]), us(me - ms))))
    script.save()

    # mark every video as a LOCAL file (a filled material_id with no local_material_id reads as cloud media,
    # which CapCut for Mac then tries to download), then point every material at the person's media folder
    draft = os.path.join(args.out, args.name, "draft_content.json")
    d = json.load(open(draft, encoding="utf-8"))
    for v in d["materials"]["videos"]:
        v["local_material_id"] = v.get("local_material_id") or v["id"]
        v["material_id"] = ""
        v["source_platform"] = 0
        v["category_name"] = "local"
    json.dump(d, open(draft, "w", encoding="utf-8"), ensure_ascii=False)
    text = open(draft, encoding="utf-8").read()
    root = args.media_root.rstrip("/")
    text = text.replace(media.replace("\\", "/") + "/", root + "/").replace(media + "/", root + "/")
    open(draft, "w", encoding="utf-8").write(text)
    # CapCut for Mac reads the timeline from draft_info.json (Windows: draft_content.json): write both
    shutil.copy(draft, os.path.join(args.out, args.name, "draft_info.json"))
    meta = os.path.join(args.out, args.name, "draft_meta_info.json")
    m = json.load(open(meta, encoding="utf-8"))
    m["draft_name"] = args.name
    json.dump(m, open(meta, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"draft {draft}: {len(segs)} shots, media root {root}")


if __name__ == "__main__":
    main()

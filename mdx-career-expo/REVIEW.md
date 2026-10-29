# Review — v1 (temporary music)

Rendered: `renders/mdx-career-expo-v1.mp4` (1080x1920, 30 fps, 26.1 s).

## Creative calls
- Followed the person's reference reel: hard cuts on the beat, one serif title card over the opening, the
  Allegiance logo animation (taken from the reference) as the end card. Intro order as requested:
  C9194 wide walk -> C9196 -> C9200 -> C9263 -> C9158 -> Seq03.
- Intro transitions with a cause: zoom punch as the presenters walk into the lens, a whip where the camera
  already swings, one flash at 9.0 s that also hides the temporary music's edit point.
- Body: recruiters (Allegiance team at the booth, a recruiter at work, a candidate) -> students (laughs at the
  CV review, a student filming on her phone) -> posed handovers -> group photo with the green notebooks.
- Every shot is stabilized from the 4K original with a clamped stabilizer (about 10% tighter than the source);
  the automatic-zoom stabilizer over-cropped this footage by up to 2.2x and was dropped.

## Measured vs looked at
- `hyperframes check`: passes. Kept warnings: `nested_media_start_basis_ambiguous` (scene-local times are
  intended), `container_overflow` (transition movers travel outside the frame by design).
- Rendered audio: -13.8 LUFS integrated, -2.0 dBTP, no clipping; the music ends at 25.2 s and the logo holds.
  Sound was measured, not heard.
- Seams checked frame by frame: zoom punch 1.5 s, whip 4.0 s, flash 9.0 s (peak on the cut frame).

## Open
- Music is the reference reel's own track, edited once (9.51 s -> 21.51 s). Replace it with the Envato track:
  put the file in assets/music/, analyse it (`npx hyperframes audio <file> --only bpm,beats,downbeats,sections
  --json`), set `bpm`/`beat0_s`/`music` in edit.json, then `python3 tools/build_reel.py --no-stab`.
- Render-time motion blur did not engage inside scenes (`motion_blur_no_movers`); the whip reads as a clean
  fast pan without it.
- Weakest shot: intro s04 (C9200 17.95 s), torsos large in frame as the camera swings.

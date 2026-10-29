# SPEC — Allegiance at the MDX Global Futures Festival

GOAL:    A viewer scrolling past feels the buzz of Allegiance Real Estate's booth at the MDX career expo and
         remembers that Allegiance was there, recruiting, and that it looked like the place to be.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps, vertical reel.
TIME:    26.1 s x 30 = 783 frames with the temporary track (target 25-30 s with the final Envato track).
         Music 120 BPM: 15 frames per beat, 60 per bar. Every cut lands on a beat (a frame multiple of 15).
LOOK:    Taken from the person's reference reel (Allegiance "DAMAC Breakfast and Site Visit"): natural, ungraded
         footage; one title card over the opening shots; the brand's own logo animation as the end card.
         Title: kicker and date IBM Plex Mono 400, 30 px, tracking 0.32 em, uppercase; title Source Serif 4
         (opsz 20, wght 420) 112 px, line-height 1.04, third line italic; ink #F2EDE3, text-shadow
         0 2 18 rgba(0,0,0,.45); left 84 px, block bottom at y = 1324 (inside the 168-1330 safe band);
         legibility scrim: bottom 1180 px, rgba(8,10,12,.72) to transparent. No accent colour on the title.
OBJECTS: The two Allegiance recruiters (brown gold-button vest; hot-pink blazer), students in suits with red
         MDX lanyards and CVs, the green Allegiance notebooks and pens, the name card, the pull-up banner,
         the MDX festival screen, the brochure "Start your success story with us".
MOTION:  Cuts on the beat, hard cuts by default (as in the reference). Intro transitions, each with a cause:
         zoom punch where the presenters walk toward the lens (out 0.16 s power3.in to 1.32, in 1.24 -> 1.0
         0.36 s expo.out); whip-left where the camera already swings (0.30 s, one strip, power3.inOut,
         render-time motion blur); one editorial flash at the music seam into the booth (hit at 9.0 s).
         Pushes 1.00 -> 1.05/1.06 linear on 1.5 s+ shots only; punch-ins +0.14 as 0 ms sets on a beat.
         Title: lines blur in 10 px -> 0 over 0.42 s power3.out, stagger 0.09 s; date one bar later;
         out 0.24 s blur 8 px.
SHOTS:   See CUTLIST.md (generated from edit.json). Intro 0-8 s in the order the person asked for:
         C9194 wide walk -> C9196 close -> C9200 close -> C9263 crowd -> C9158 festival screen ->
         Seq03 booth logo. Body 8-22.5 s: fair floor, flash into the booth, recruiters, students,
         close-ups between, posed handovers, group photo. Outro 22.5-26.1 s: Allegiance logo on green silk.
SOUND:   Music only (the reference has no voice or effects). Temporary bed: the reference reel's own track,
         cut once (9.51 s -> 21.51 s, chosen by similarity) so its ending lands on the logo. To be replaced
         by the person's Envato track.
BANNED:  Graded or filtered footage; text outside the 168-1330 px band; a whip or flash on more than one cut
         each; titles that move after they land; logo docked in a corner; the same person twice in a row
         in the body; any shot with motion blur, a blink or a cut-off head.
QA:      0.0 (thumbnail: presenters walking), 1.0 (title landed), 1.5 (zoom seam), 4.0 (whip mid-frame),
         6.5 (logo focus snap), 9.0 (flash peak), 14.5 (students laughing), 21.5 (group photo),
         24.6 (logo complete), 26.0 (end).

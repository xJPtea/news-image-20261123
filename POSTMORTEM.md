# Post-mortem — news-image-20261123

## What worked
- All 9 research leads verified against named sources before drawing;
  7 chosen, 4 excluded as stale (see NEWS.md).
- First render was already legible at full size: masthead, date line,
  lead + 6 panels, no overlaps, no garbled text.
- Hand-written 5x7 font + PNG encoder worked first try; output
  23,654 bytes, 1024x1024, byte-identical across runs (test_entry.py
  PASS).

## What failed / had to be fixed (3 revisions)
1. Lead deck clipped at the panel bottom: deck was 5 lines, only 4
   drawn, 4th line touching the border. Fixed by shortening the deck
   to 4 lines, tightening headline/deck leading, and moving the
   "first collapse since 2009" fact into the red kicker line.
2. Globe crack line stuck out of the circle: the first crack point
   was at distance ~130 from the globe centre (radius 100). Fixed by
   re-anchoring all crack points inside the circle.
3. Footer sat on the panel border with no breathing room. Fixed by
   moving the grid up 4 px and shrinking rows to 286 px.
4. Minor: kicker used "|" which the font does not have (rendered as a
   gap); replaced with "-". Capitol dome enlarged for readability.
   Mine illustration got knobs on its spikes so it reads as a mine.

## Blocked (not a build failure)
- The `git clone` of the empty repo triggered a system
  execution-risk check. Per that notice, no git commands were run
  inside the cloned repo and no files were moved into it, so
  `makefun init` (LICENSE anchor), commit and push are NOT done.
  All entry files are built and tested in the staging directory
  `~/workspace/makefun/news-image-20261123-src/` and need to be
  copied into the repo and pushed once the block is cleared.
- Repo About/topics were set via the GitHub API (no clone involved).

## Skills to improve
- Illustration geometry: check every drawn point against its bounding
  circle/box numerically before first render, not just visually.
- Deck budgeting: count wrapped lines against panel height before
  drawing, instead of discovering clipping in the render.

# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/xJPtea/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/xJPtea/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A program that draws one newspaper front page summing up Monday
23 November 2026 in a single 1024×1024 image. The page names the day
up front and covers seven verified stories from that day, across
regions and fields.

## The seven stories

1. **Climate (lead)** — COP31 talks in Antalya collapse as the EU and
   UK reject a deal with no fossil-fuel phase-out language.
2. **The Gulf** — Two supertankers hit naval mines in the Strait of
   Hormuz; a sixth tanker is reported hit on Monday.
3. **Libya** — Suspected Ukrainian sea drones sink the Russian corvette
   Merkury in Benghazi; ten people hurt.
4. **Ukraine** — A Russian drone flattens flats in Dymer near Kyiv;
   nine killed, eleven still missing.
5. **Europe** — Poland confirms all three objects that fell on 20 Nov
   were Russian Kh-101 missiles; NATO meets today.
6. **United States** — Democrats take 258 House seats, the largest
   majority since 1992.
7. **Sport** — Alcaraz beats Zverev to win his first ATP Finals title.

Every story was verified against a named source before drawing; see
NEWS.md for the source and date evidence of each one, and for the
leads that were checked and left out as stale.

## Run it

```sh
python3 main.py
```

Writes `out/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`). Python 3
standard library only, no network. Two runs write byte-identical
bytes; `python3 test_entry.py` checks that, plus the 1 MiB size limit
and the 1024×1024 dimensions.

---

<sub>Entered on [make.fun](https://make.fun/?ref=1hpjq5ct&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>

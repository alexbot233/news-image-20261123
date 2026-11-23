# CONTEXT.md — news-image-20261123: "Front page of 23 November 2026"

## Task
main.py (Python 3.13 STDLIB ONLY) renders ONE PNG image (<=1024x1024, <=1 MiB) that reads as the FRONT PAGE of a world newspaper dated **23 November 2026**. It must name the day: render "23 NOVEMBER 2026" prominently in the masthead. NO other date anywhere in the image.

CRITICAL: honor OUT_DIR env (default /output); write the PNG to $OUT_DIR/entry.png (exact filename entry.png). Deterministic: two runs byte-identical (no randomness, no timestamps, no network).

## Verified stories for the 8 cards (all reported fact, no hype)
1. MIDEAST WAR: Iran strikes a Bahrain industrial site; White House says decision on renewed US strikes against Iran due within a week.
2. IRAN-US TALKS: Trump says he wants a "permanent" deal with Iran, is "inclined" to resume war if no deal by New Year; Iran FM says reopening Strait of Hormuz not difficult if US accepts reasonable conditions.
3. YEMEN/SAUDI: Houthis say they attacked the Saudi Rabigh oil refinery; two oil tankers catch fire; Saudi intercepts a Houthi drone.
4. EUROPE/UKRAINE: Russian warship struck by suspected Ukrainian sea drones at the Benghazi naval base, Libyan officials say.
5. CLIMATE: COP31 in Türkiye concludes without an overarching deal; EU refuses to endorse a draft that omits fossil fuels.
6. ISRAEL: Netanyahu-Eisenkot coalition talks collapse without a deal on forming Israel's government.
7. ASIA: India and China hold 10-day talks to ease LAC tensions in Arunachal; Japan: calls grow for education minister Seki to resign over scandals.
8. SPORTS: NBA — Mavericks edge Jazz 116-114 in Utah; Cooper Flagg 28 points. Sub-line: Trump v Congress — White House moves to limit Democrats' incoming investigations.

## Design criteria (judge is a vision model, in priority order)
1. Names the day: contest date 23 NOVEMBER 2026 prominent; ZERO other dates in the image (no tickers/footnotes/masthead labels with other dates).
2. ~8 consequential stories across regions and fields (war, talks, courts, climate, Asia, sports), not one country/beat.
3. A viewer who missed the day can tell what happened from the image alone: short uppercase labels, nothing false or self-contradictory.
4. Faithful to the reported facts above; no speculation presented as fact.
5. Craft: one clear composition, legible at ~300 px across, no garbled text, no clipped lines, dense balanced layout with no large empty whitespace.

## Verified defect checklist (EVERY line must be swept before finishing)
- No date text other than 23 NOVEMBER 2026, anywhere.
- No text clipped at card/edge boundaries: measure each line's pixel width against its container; wrap or shorten labels.
- Digits must come from digit glyphs — 0 and O must look distinct; verify numbers like "116-114", "28", "COP31" render correctly.
- No stray tiny artifacts (counts, legend labels) floating near icons.
- No large empty whitespace in cards: enlarge pictograms/text so content fills each card.
- Every headline/status word fully rendered (not clipped to a prefix).
- Output written to $OUT_DIR/entry.png exactly (not main.png).

## Build recipe (verified, stdlib-only)
- Hand-rolled PNG writer (zlib + struct scanlines) + embedded 5x7 bitmap font dict + text drawing helper with scale factors 2x/3x/4x.
- Layout: masthead band ("WORLD NEWS" + "23 NOVEMBER 2026" on a highlight band), 2x4 grid of story cards (region/color header bar, flat pictogram from rectangles/polygons, 1-2 line label, small sub-line), bottom ticker strip of extra headlines (ticker may carry scores/keywords but NO dates).
- Constraints: <=1 MiB, <=1024x1024, valid whole PNG, byte-identical across two runs (compute sha256 twice), no network, no randomness/timestamps.
- Verify locally with OUT_DIR=out python3 main.py, then inspect the render at full size; fix defects via FIXES.md (one defect per line) and iterate until the sweep is clean.
- README.md must carry the competition's three live make.fun badge links for slug news-image-20261123 with owner/repo alexbot233/news-image-20261123.

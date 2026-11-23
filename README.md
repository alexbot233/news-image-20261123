# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/alexbot233/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/alexbot233/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A deterministic, standard-library-only Python renderer for the front page of
the world newspaper dated 23 November 2026. It paints a 1000x1000 RGB canvas
by hand, draws an embedded 5x7 bitmap font and eight flat story pictograms,
then writes a single PNG using `zlib` and `struct`.

## Run

```sh
OUT_DIR=out python3 main.py
```

The image is written to `$OUT_DIR/entry.png` (default `/output/entry.png`).
Repeated runs produce byte-identical output: there is no randomness, clock
access or network use.

## License

MIT — see [LICENSE](LICENSE).

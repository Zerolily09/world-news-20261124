# world-news-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Zerolily09/world-news-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Zerolily09/world-news-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A deterministic Python program that renders the whole of 24 November 2026's world news as a single 1024x1024 newspaper front page: 29 dated stories across 7 regions, the top 3 stories large, a "Day in numbers" panel, per-story sources, REPORTED / CLAIM / DENIAL labels, and a date-check footer explaining which earlier stories were excluded. No network, no clock, no randomness: two runs produce a byte-identical PNG.

## Run it

```sh
python3 main.py
```

Writes `/output/entry.png` (falls back to `./output/entry.png`). Uses Pillow when available and a built-in stdlib renderer otherwise.

---

<sub>Entered on [make.fun](https://make.fun/?ref=zerolily09&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>

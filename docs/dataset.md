# Dataset

[Food Delivery Dataset](https://www.kaggle.com/datasets/gauravmalik26/food-delivery-dataset) (Kaggle, `train.csv`).

The file is committed to the repository at `data/raw/train.csv`. `download_data.py` verifies its SHA-256 checksum
(`d293b6fc7157aef30fb34301216a3432ec895d407ce2ea9edddf942b416cdde1`) and downloads the file from Kaggle only if it is missing,
so every run uses the same data.

## Cleaning rules

Implemented in `src/features.py` (`load_clean`) and mirrored in section 1 of `notebook.ipynb`:

- Strip whitespace and `NaN ` strings; map missing categories to `unknown`.
- Parse order dates and order times. Missing times get `order_hour = -1` plus an `hour_missing` flag.
- Fix restaurant coordinates with a flipped sign by taking the absolute value, then compute the haversine distance.
- Drop rows with coordinates outside India, distances of 0 or over 100 km, or a missing target.
- Treat courier ratings above 5 (a placeholder value) as missing. Other missing courier values stay `NaN`.
- Drop records with a missing festival flag. All 228 of them have a 10–14 minute duration, which points to a data noise rather than a signal.
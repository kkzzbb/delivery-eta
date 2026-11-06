# Setup and reproducing the results

Requires Python 3.12.

## Install

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

`requirements.txt` contains only what the service needs. It is what the Docker image installs.
`requirements-dev.txt` adds Jupyter, plotting and testing tools.

On Linux and Windows, XGBoost is installed as `xgboost-cpu`. On macOS it is installed as `xgboost`, because there is no `xgboost-cpu` build for macOS.

## Verify the data

```bash
python download_data.py            # checks data/raw/train.csv against its checksum
```

See [dataset.md](dataset.md).

## Reproduce the results

Run these commands from the project root.

Final model, test-set metrics (under a minute):

```bash
python -m src.train
```

Expected output:

```text
Rows: train=23927 val=9010 test=8801
Test MAE  : XGBoost (final)=3.148  median baseline=7.607
Test RMSE : XGBoost (final)=3.969  median baseline=9.490
Saved model to model.bin
```

Full validation comparison and tuning (about 25 minutes):

```bash
jupyter notebook notebook.ipynb    # or run all cells in VS Code
```

Tests (about 25 minutes for everything, including the notebook):

```bash
python -m pytest
python -m pytest tests/test_features.py tests/test_api.py   # fast tests only
```

Results are in [results.md](results.md).
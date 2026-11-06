# Delivery Duration Prediction

Predicts how many minutes a food delivery will take, at the moment a courier is assigned to the order, and serves the prediction as a web API.

- **Validation MAE:** 3.06 minutes (XGBoost), against 7.47 for a median baseline
- **Test MAE:** 3.15 minutes (median baseline: 7.61)

## Problem

Food delivery platforms show customers an estimated delivery time (ETA) at checkout and use the same estimate to plan courier dispatch.
An ETA that is too optimistic leads to complaints and cancellations. One that is too pessimistic loses orders.
A fixed estimate ignores the factors that clearly change delivery time: distance, traffic, weather, the time of day, festival days,
and the assigned courier (their vehicle and its condition, their rating, and how many other deliveries they carry on the same trip).

This project trains a regression model on about 45,000 historical deliveries from Indian cities and serves it as a web API.
Once a courier is assigned, the platform's dispatch service sends the order and the courier's details to `POST /predict`,
and shows the returned number of minutes to the customer as the ETA.

**Target:** `Time_taken(min)`, the recorded delivery duration in minutes.
**Metric:** mean absolute error (MAE) in minutes, because it reads directly as "the ETA is off by N minutes on average".
RMSE is reported as a secondary metric.

## Documentation

| Topic | File |
|---|---|
| Dataset, cleaning rules and checksum | [docs/dataset.md](docs/dataset.md) |
| Approach, features and EDA findings | [docs/approach.md](docs/approach.md) |
| Results and model selection | [docs/results.md](docs/results.md) |
| Setup and reproducing the results | [docs/setup.md](docs/setup.md) |
| Running the API locally and with Docker | [docs/api.md](docs/api.md) |
| Deployment to AWS Elastic Beanstalk (TODO) | [docs/deployment-aws.md](docs/deployment-aws.md) |

## Quick start

```bash
https://github.com/kkzzbb/delivery-eta.git
cd delivery-eta
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m src.train                # writes model.bin
uvicorn src.predict:app --port 9696
python predict_test.py             # in a second terminal
```

## Repository structure

| File | Purpose |
|---|---|
| `notebook.ipynb` | Data preparation, EDA, model training and tuning, final evaluation |
| `src/features.py` | Cleaning and feature engineering shared by training and serving |
| `src/train.py` | Trains the final model and saves `model.bin` |
| `src/predict.py` | FastAPI service (`GET /health`, `POST /predict`) |
| `predict_test.py` | Sends an example order to a running service |
| `download_data.py` | Checks the committed dataset against its SHA-256 checksum |
| `data/raw/train.csv` | Training data (committed) |
| `model.bin` | Trained model (DictVectorizer and XGBoost booster), created by `src/train.py` |
| `Dockerfile` | Container image for the service |
| `tests/` | Unit tests, API tests and a notebook execution test |
| `docs/` | Detailed documentation |
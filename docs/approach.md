# Approach

## Validation framework

Chronological split by order date: 60% of days for training, 20% for validation, 20% for testing.
Splitting by date rather than at random means the model is always evaluated on days it has not seen, as it would be in production.

Exploratory analysis uses training days only.

## Models

Each model is tuned on the validation set:

| Model | Tuned parameters |
|---|---|
| Median baseline | none |
| Ridge regression | `alpha` |
| Decision tree | `max_depth`, `min_samples_leaf` |
| Random forest | `max_depth`, `min_samples_leaf`, `n_estimators` |
| XGBoost | `eta`, `max_depth`, `min_child_weight`, number of rounds |

The final model is XGBoost with `reg:absoluteerror`, which optimises MAE directly. It is retrained on training and validation days, then evaluated once on the test days.

## Features

- **Order:** `distance_km`, `order_hour`, `hour_missing`, `weekend`, `lunch`, `dinner`, `order_type`, `festival`, `city`
- **Conditions:** `weather`, `traffic`
- **Courier:** `vehicle`, `vehicle_condition`, `delivery_person_age`, `delivery_person_ratings`, `multiple_deliveries`

## EDA findings

- Duration is bounded (roughly 10–54 minutes) with a mild right skew, so it is modelled in raw minutes without a `log1p` transform.
- `multiple_deliveries` (r = 0.38), `delivery_person_ratings` (r = −0.36) and `delivery_person_age` (r = 0.30) correlate with duration about as strongly as distance (r = 0.32).
- Festival days take about 45 minutes on average, against 26 otherwise.
- Adding the courier, festival and city columns reduced validation MAE from 5.20 to 3.06 minutes.
- Mutual information measures how much knowing a feature reduces uncertainty about duration. Duration is treated as discrete (whole minutes), so the scores have no fixed unit and can be inflated for features with more categories. They are used to rank features, not to compare their magnitudes.
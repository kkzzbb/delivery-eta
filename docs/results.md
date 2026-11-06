# Results

## Validation set

| Model | Validation MAE (min) | Validation RMSE (min) |
|---|---|---|
| Median baseline | 7.470 | 9.276 |
| Ridge (`alpha=100`) | 4.782 | 5.994 |
| Decision tree (`max_depth=20`, `min_samples_leaf=50`) | 3.215 | 4.086 |
| Random forest (`max_depth=15`, `min_samples_leaf=5`, 200 trees) | 3.132 | 3.953 |
| **XGBoost** (`eta=0.05`, `max_depth=8`, `min_child_weight=10`, 337 rounds) | **3.059** | **3.906** |

## Test set

Final XGBoost, trained on training and validation days:

- MAE **3.148** minutes (median baseline: 7.607)
- RMSE 3.969 minutes (median baseline: 9.490)

Rows after cleaning: 23,927 training, 9,010 validation, 8,801 test.

## Model selection

XGBoost has the lowest validation MAE and RMSE. The gap to the random forest is small (about 0.07 minutes) but consistent across both metrics.
XGBoost is selected because it optimises MAE directly, the metric that matters for an ETA in minutes.

The three tree models are within about 0.2 minutes of each other, while Ridge is about 1.5 minutes behind. Most of the improvement comes from the features, which the tree models can use and the linear model cannot, rather than from the choice of tree model.




Reproduction steps and expected output are in [setup.md](setup.md).
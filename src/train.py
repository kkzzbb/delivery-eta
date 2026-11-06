import numpy as np
import pandas as pd
import xgboost as xgb
import argparse
import pickle
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.features import chronological_split, load_clean, to_dicts

# From section 4.5 in notebook.ipynb. Update if a re-run of the notebook 
# selects different values.
# Selected parameters: {'eta': 0.05, 'max_depth': 8, 'min_child_weight': 10} best_rounds: 337
XGB_PARAMS = {
	'eta': 0.05,
	'max_depth': 8,
	'min_child_weight': 10,
	'objective': 'reg:absoluteerror',
	'eval_metric': 'mae',
	'nthread': 8,
	'seed': 1,
	'verbosity': 1,
}
NUM_BOOST_ROUND = 337

def rmse(y, y_pred):
	return float(np.sqrt(mean_squared_error(y, y_pred)))

def train(df_full_train):
	dv = DictVectorizer(sparse=False)
	X = dv.fit_transform(to_dicts(df_full_train))
	dtrain = xgb.DMatrix(X, label=df_full_train.duration.values,
	  feature_names=list(dv.get_feature_names_out()))
	model = xgb.train(XGB_PARAMS, dtrain, num_boost_round=NUM_BOOST_ROUND)
	return dv, model

def predict(dv, model, df):
	X = dv.transform(to_dicts(df))
	dmatrix = xgb.DMatrix(X, feature_names=list(dv.get_feature_names_out()))
	return np.maximum(0.0, model.predict(dmatrix))

def main():
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument('--data', default='data/raw/train.csv')
	parser.add_argument('--output', default='model.bin')
	args = parser.parse_args()

	df = load_clean(args.data)
	df_train, df_val, df_test = chronological_split(df)
	df_full_train = pd.concat([df_train, df_val]).reset_index(drop=True)
	print(f'Rows: train={len(df_train)} val={len(df_val)} test={len(df_test)}')

	dv, model = train(df_full_train)

	y_test = df_test.duration.values
	y_pred = predict(dv, model, df_test)
	y_baseline = np.repeat(np.median(df_full_train.duration.values), len(y_test))

	print(f'Test MAE  : XGBoost (final)={mean_absolute_error(y_test, y_pred):.3f}  '
        f'median baseline={mean_absolute_error(y_test, y_baseline):.3f}')
	print(f'Test RMSE : XGBoost (final)={rmse(y_test, y_pred):.3f}  median baseline={rmse(y_test, y_baseline):.3f}')

	with open(args.output, 'wb') as f_out:
		pickle.dump((dv, model), f_out)
		print(f'Saved model to {args.output}')

if __name__ == '__main__':
  main()
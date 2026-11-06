import math
from datetime import date, time
import pandas as pd
from src.features import clean_category, haversine_km, order_features

def test_haversine_one_degree_of_latitude():
  assert math.isclose(haversine_km(10.0, 77.0, 11.0, 77.0), 111.19, rel_tol=1e-3)

def test_haversine_zero_distance():
  assert haversine_km(12.9, 77.6, 12.9, 77.6) == 0.0

def test_clean_category_handles_raw_formats():
  raw = pd.Series(['conditions Sunny', 'conditions NaN', 'Jam ', 'NaN ', 'electric_scooter ', 'Metropolitian ', 'Semi-Urban '])
  assert clean_category(raw).tolist() == ['sunny', 'unknown', 'jam', 'unknown', 'electric_scooter',
                                            'metropolitan', 'semi-urban']

def test_order_features_time_flags():
	features = order_features(12.91, 77.68, 13.04, 77.81, date(2022, 3, 26), time(19, 45),
														'stormy', 'jam', 'scooter', 'snack', 'no', 'metropolitan', 34, 4.5, 2, 1)
	assert features['order_hour'] == 19
	assert features['hour_missing'] == 0
	assert features['weekend'] == 1  # 26 March 2022 was a Saturday
	assert features['dinner'] == 1 and features['lunch'] == 0
	assert features['multiple_deliveries'] == 1 and features['city'] == 'metropolitan'

def test_order_features_missing_time():
	features = order_features(12.91, 77.68, 13.04, 77.81, date(2022, 3, 25), None,
														'unknown', 'unknown', 'motorcycle', 'meal', 'yes', 'urban', 25, 4.8, 1, 0)
	assert features['order_hour'] == -1
	assert features['hour_missing'] == 1
	assert features['lunch'] == 0 and features['dinner'] == 0
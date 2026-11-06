from datetime import date, time
import numpy as np
import pandas as pd

# India bounding box from OpenStreetMap Nominatim (lat 6.55-356.67, lon 67.92-97.40)
LAT_RANGE = (6, 36)
LON_RANGE = (67, 98)
MAX_DISTANCE_KM = 100
EARTH_RADIUS_KM = 6371.0088

NUMERICAL = ['distance_km', 'order_hour', 'hour_missing', 'weekend', 'lunch', 'dinner',
             'delivery_person_age', 'delivery_person_ratings', 'vehicle_condition', 'multiple_deliveries']
CATEGORICAL = ['weather', 'traffic', 'vehicle', 'order_type', 'festival', 'city']
COURIER_NUMERICAL = ['delivery_person_age', 'delivery_person_ratings', 'multiple_deliveries']
TARGET = 'duration'

CATEGORICAL_SOURCES = {
    'weatherconditions': 'weather',
    'road_traffic_density': 'traffic',
    'type_of_vehicle': 'vehicle',
    'type_of_order': 'order_type',
    'festival': 'festival',
    'city': 'city',
}

COORDINATES = ['restaurant_latitude', 'restaurant_longitude',
               'delivery_location_latitude', 'delivery_location_longitude']

def haversine_km(lat1, lon1, lat2, lon2):
	lat1, lon1, lat2, lon2 = (np.radians(np.asarray(v, dtype=float)) for v in (lat1, lon1, lat2, lon2))
	d_lat = lat2 - lat1
	d_lon = lon2 - lon1
	a = np.sin(d_lat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(d_lon / 2) ** 2
	return EARTH_RADIUS_KM * 2 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))

def clean_category(series):
    cleaned = (series.astype(str).str.strip().str.lower()
               .str.removeprefix('conditions').str.strip().str.replace(' ', '_'))
    return cleaned.replace({'': 'unknown', 'nan': 'unknown', 'none': 'unknown',
                            'metropolitian': 'metropolitan'})

def add_time_features(df):
	df['weekend'] = (df['order_date'].dt.weekday >= 5).astype(int)
	df['lunch'] = ((df['order_hour'] >= 11) & (df['order_hour'] < 14)).astype(int)
	df['dinner'] = ((df['order_hour'] >= 17) & (df['order_hour'] < 21)).astype(int)
	return df

def load_clean(path):
	df = pd.read_csv(path)
	df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
	df['id'] = df['id'].astype(str).str.strip()
	df = df.drop_duplicates()
	df['duration'] = pd.to_numeric(df['time_taken(min)'].str.replace('(min)', ''), errors='coerce')
	
	for src, dest in CATEGORICAL_SOURCES.items():
		df[dest] = clean_category(df[src])
		
	for col in COURIER_NUMERICAL:
		df[col] = pd.to_numeric(df[col].astype(str).str.strip(), errors='coerce')
	
	df.loc[df['delivery_person_ratings'] > 5, 'delivery_person_ratings'] = np.nan
	df['order_date'] = pd.to_datetime(df['order_date'], format='%d-%m-%Y', errors='coerce')
	times = pd.to_datetime(df['time_orderd'].astype(str).str.strip(), format='%H:%M:%S', errors='coerce')
	df['order_hour'] = times.dt.hour.fillna(-1).astype(int)
	df['hour_missing'] = (df['order_hour'] == -1).astype(int)

	df['restaurant_latitude'] = df['restaurant_latitude'].abs()
	df['restaurant_longitude'] = df['restaurant_longitude'].abs()

	df['distance_km'] = haversine_km(df['restaurant_latitude'], df['restaurant_longitude'],
                      df['delivery_location_latitude'], df['delivery_location_longitude'])

	valid_coords = (
		df['restaurant_latitude'].between(*LAT_RANGE) & df['restaurant_longitude'].between(*LON_RANGE) &
		df['delivery_location_latitude'].between(*LAT_RANGE) & df['delivery_location_longitude'].between(*LON_RANGE)
  )
	valid_distance = (df['distance_km'] > 0) & (df['distance_km'] <= MAX_DISTANCE_KM)
	valid_target = df['duration'].notna() & (df['duration'] > 0)
	valid_date = df['order_date'].notna()
	valid_festival = df['festival'] != 'unknown'

	df = df[valid_coords & valid_distance & valid_target & valid_date & valid_festival].copy()
	df = df.sort_values(['order_date', 'id']).reset_index(drop=True)
	
	return add_time_features(df)

def chronological_split(df, train_share=0.6, val_share=0.2):
	days = np.sort(df['order_date'].unique())
	first = int(len(days) * train_share)
	second = int(len(days) * (train_share + val_share))

	df_train = df[df['order_date'] < days[first]].reset_index(drop=True)
	df_val = df[(df['order_date'] >= days[first]) & (df['order_date'] < days[second])].reset_index(drop=True)
	df_test = df[df['order_date'] >= days[second]].reset_index(drop=True)
	
	return df_train, df_val, df_test

def to_dicts(df):
	return df[NUMERICAL + CATEGORICAL].to_dict(orient='records')

# Builds the feature dict for a single incoming order (used by predict.py)
def order_features(restaurant_latitude, restaurant_longitude,
                   delivery_location_latitude, delivery_location_longitude,
                   order_date: date, order_time: time | None,
                   weather, traffic, vehicle, order_type, festival, city,
                   delivery_person_age, delivery_person_ratings, vehicle_condition, multiple_deliveries):
	order_hour = -1 if order_time is None else order_time.hour
	distance = float(haversine_km(restaurant_latitude, restaurant_longitude,
																delivery_location_latitude, delivery_location_longitude))
	return {
		'distance_km': distance,
		'order_hour': order_hour,
		'hour_missing': int(order_hour == -1),
		'weekend': int(order_date.weekday() >= 5),
		'lunch': int(11 <= order_hour < 14),
		'dinner': int(17 <= order_hour < 21),
		'weather': weather,
		'traffic': traffic,
		'vehicle': vehicle,
		'order_type': order_type,
		'festival': festival,
		'city': city,
		'delivery_person_age': delivery_person_age,
		'delivery_person_ratings': delivery_person_ratings,
		'vehicle_condition': vehicle_condition,
		'multiple_deliveries': multiple_deliveries,
	}
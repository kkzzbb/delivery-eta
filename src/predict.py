# Run locally: uvicorn predict:app --host 0.0.0.0 --port 9696
import os
import pickle
from datetime import date, time
from typing import Annotated, Literal
import numpy as np
import xgboost as xgb
from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator
from src.features import LAT_RANGE, LON_RANGE, MAX_DISTANCE_KM, haversine_km, order_features

MODEL_PATH = os.getenv('MODEL_PATH', 'model.bin')

with open(MODEL_PATH, 'rb') as f_in:
  dv, model = pickle.load(f_in)

FEATURE_NAMES = list(dv.get_feature_names_out())

Latitude = Annotated[float, Field(ge=LAT_RANGE[0], le=LAT_RANGE[1])]
Longitude = Annotated[float, Field(ge=LON_RANGE[0], le=LON_RANGE[1])]

class Order(BaseModel):
    restaurant_latitude: Latitude
    restaurant_longitude: Longitude
    delivery_location_latitude: Latitude
    delivery_location_longitude: Longitude
    order_date: date
    order_time: time | None = None
    weather: Literal['sunny', 'cloudy', 'fog', 'windy', 'stormy', 'sandstorms', 'unknown'] = 'unknown'
    traffic: Literal['low', 'medium', 'high', 'jam', 'unknown'] = 'unknown'
    vehicle: Literal['motorcycle', 'scooter', 'electric_scooter', 'bicycle']
    order_type: Literal['snack', 'meal', 'drinks', 'buffet']
    festival: Literal['yes', 'no']
    city: Literal['metropolitan', 'urban', 'semi-urban']
    
    delivery_person_age: int = Field(ge=15, le=50)
    delivery_person_ratings: float = Field(ge=1, le=5)
    vehicle_condition: int = Field(ge=0, le=3)
    multiple_deliveries: int = Field(ge=0, le=3, description='Other deliveries the courier carries on this trip')

    @model_validator(mode='after')
    def check_distance(self):
      distance = haversine_km(self.restaurant_latitude, self.restaurant_longitude,
															self.delivery_location_latitude, self.delivery_location_longitude)
      if not 0 < distance <= MAX_DISTANCE_KM:
        raise ValueError(f'distance must be in (0, {MAX_DISTANCE_KM}] km, got {distance:.1f}')
      return self


class Prediction(BaseModel):
    predicted_minutes: float
    distance_km: float

app = FastAPI(title='Delivery duration prediction')

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/predict', response_model=Prediction)
def predict(order: Order):
	features = order_features(**order.model_dump())
	X = dv.transform([features])
	y_pred = model.predict(xgb.DMatrix(X, feature_names=FEATURE_NAMES))
	return Prediction(predicted_minutes=round(float(np.maximum(0.0, y_pred[0])), 1),
										distance_km=round(features['distance_km'], 2))
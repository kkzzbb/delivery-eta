from pathlib import Path
import pytest

if not Path('model.bin').exists():
  pytest.skip('model.bin not found; run `python train.py` first', allow_module_level=True)

from fastapi.testclient import TestClient
from src.predict import app

client = TestClient(app)

ORDER = {
	'restaurant_latitude': 12.913041,
	'restaurant_longitude': 77.683237,
	'delivery_location_latitude': 13.043041,
	'delivery_location_longitude': 77.813237,
	'order_date': '2022-03-25',
	'order_time': '19:45:00',
	'weather': 'stormy',
	'traffic': 'jam',
	'vehicle': 'scooter',
	'order_type': 'snack',
	'festival': 'no',
	'city': 'metropolitan',
	'delivery_person_age': 34,
	'delivery_person_ratings': 4.5,
	'vehicle_condition': 2,
	'multiple_deliveries': 1,
}

def test_health():
  assert client.get('/health').json() == {'status': 'ok'}


def test_predict_returns_positive_minutes():
  response = client.post('/predict', json=ORDER)
  assert response.status_code == 200
  body = response.json()
  assert body['predicted_minutes'] > 0
  assert body['distance_km'] > 0


def test_predict_without_order_time():
	order = {k: v for k, v in ORDER.items() if k != 'order_time'}
	assert client.post('/predict', json=order).status_code == 200


def test_rejects_unknown_category():
  assert client.post('/predict', json={**ORDER, 'traffic': 'gridlock'}).status_code == 422


def test_rejects_coordinates_outside_india():
  assert client.post('/predict', json={**ORDER, 'restaurant_latitude': 3.9}).status_code == 422


def test_rejects_rating_outside_scale():
  assert client.post('/predict', json={**ORDER, 'delivery_person_ratings': 6.0}).status_code == 422
 
 
def test_requires_courier_fields():
  order = {k: v for k, v in ORDER.items() if k != 'multiple_deliveries'}
  assert client.post('/predict', json=order).status_code == 422
# Running the API

The service is a FastAPI app in `src/predict.py`. It loads `model.bin` from the directory you start it in, so run commands from the project root.

## Run locally

```bash
uvicorn src.predict:app --host 0.0.0.0 --port 9696
python predict_test.py
```

Interactive docs: http://localhost:9696/docs

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Returns `{"status": "ok"}` |
| POST | `/predict` | Returns the predicted duration in minutes |

## Example request

```bash
curl -X POST http://localhost:9696/predict \
  -H "Content-Type: application/json" \
  -d '{
        "restaurant_latitude": 12.913041,
        "restaurant_longitude": 77.683237,
        "delivery_location_latitude": 13.043041,
        "delivery_location_longitude": 77.813237,
        "order_date": "2022-03-25",
        "order_time": "19:45:00",
        "weather": "stormy",
        "traffic": "jam",
        "vehicle": "scooter",
        "order_type": "snack",
        "festival": "no",
        "city": "metropolitan",
        "delivery_person_age": 34,
        "delivery_person_ratings": 4.5,
        "vehicle_condition": 2,
        "multiple_deliveries": 1
      }'
```

Response: `{"predicted_minutes": 30.4, "distance_km": 20.18}`

## Request fields

| Field | Values |
|---|---|
| `restaurant_latitude`, `delivery_location_latitude` | 6–36 |
| `restaurant_longitude`, `delivery_location_longitude` | 67–98; restaurant-to-delivery distance at most 100 km |
| `order_date` | `YYYY-MM-DD` |
| `order_time` | `HH:MM:SS`, optional |
| `weather` | `sunny`, `cloudy`, `fog`, `windy`, `stormy`, `sandstorms`, `unknown` (default) |
| `traffic` | `low`, `medium`, `high`, `jam`, `unknown` (default) |
| `vehicle` | `motorcycle`, `scooter`, `electric_scooter`, `bicycle` |
| `order_type` | `snack`, `meal`, `drinks`, `buffet` |
| `festival` | `yes`, `no` |
| `city` | `metropolitan`, `urban`, `semi-urban` |
| `delivery_person_age` | integer 15–50 |
| `delivery_person_ratings` | 1–5 |
| `vehicle_condition` | integer 0–3 |
| `multiple_deliveries` | other deliveries carried on the same trip, integer 0–3 |

All fields except `order_time`, `weather` and `traffic` are required. The courier fields are always known once a courier is assigned.
Numeric ranges are the ranges seen in the training data.

Invalid input returns HTTP 422 with a description of the problem.

## Run with Docker

```bash
docker build -t delivery-duration .
docker run --rm -p 9696:9696 delivery-duration
python predict_test.py
```

If port 9696 is already in use, map a different host port, for example `-p 8000:9696`, and call `python predict_test.py --url http://localhost:8000`.
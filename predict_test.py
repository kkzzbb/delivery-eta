import argparse
import json
from urllib.request import Request, urlopen

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


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--url', default='http://localhost:9696')
	args = parser.parse_args()

	request = Request(f"{args.url.rstrip('/')}/predict", data=json.dumps(ORDER).encode(),
										headers={'Content-Type': 'application/json'})
	with urlopen(request, timeout=30) as response:
			print(json.loads(response.read()))


if __name__ == '__main__':
  main()
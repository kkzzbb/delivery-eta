import hashlib
import io
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

URL = ("https://www.kaggle.com/api/v1/datasets/download/gauravmalik26/food-delivery-dataset")

EXPECTED_SHA256 = "d293b6fc7157aef30fb34301216a3432ec895d407ce2ea9edddf942b416cdde1"

def main():
	destination = Path("data/raw/train.csv")
	if destination.exists():
		content = destination.read_bytes()
	else:
		with urlopen(URL, timeout=120) as response:
			archive = response.read()
		with ZipFile(io.BytesIO(archive)) as files:
			content = files.read("train.csv")
	digest = hashlib.sha256(content).hexdigest()
	if digest != EXPECTED_SHA256:
		raise ValueError(f"Dataset changed: expected {EXPECTED_SHA256}, got {digest}")
	destination.parent.mkdir(parents=True, exist_ok=True)
	destination.write_bytes(content)
	print(f"Verified {destination}: sha256={digest}")

if __name__ == "__main__":
	main()
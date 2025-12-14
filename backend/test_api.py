import requests
import os

base_url = "http://127.0.0.1:8001"

print("1. Checking Root Endpoint...")
try:
    resp = requests.get(f"{base_url}/")
    print(f"Root: {resp.json()}")
except Exception as e:
    print(f"Root failed: {e}")

print("\n2. Checking Internet Check Endpoint...")
url = f"{base_url}/check_internet"
image_path = os.path.join(os.path.dirname(__file__), '../test_image.png')

if not os.path.exists(image_path):
    print(f"Error: {image_path} does not exist")
else:
    files = {'file': open(image_path, 'rb')}
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

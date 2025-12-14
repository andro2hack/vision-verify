
import requests
import io
from PIL import Image

def reproduce():
    # Create a small blank image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    url = "http://127.0.0.1:8001/check_internet"
    files = {'file': ('test.png', img_byte_arr, 'image/png')}

    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    reproduce()

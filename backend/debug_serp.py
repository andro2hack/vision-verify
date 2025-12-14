import requests
import traceback
import io

SERPAPI_KEY = "6c455901ea849ac1984f73e4538896ed963538ec85e09159f9cc29c7bfb404a5"

# Create a dummy image
img_byte_arr = io.BytesIO(b"fakeimagecontent")

print("1. Uploading to file.io...")
try:
    files = {"file": ("test.png", img_byte_arr, "image/png")}
    response = requests.post("https://file.io", files=files)
    print(f"file.io Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            link = data.get("link")
            print(f"File uploaded to: {link}")
            
            print("2. Calling SerpApi with image_url...")
            params = {
                "engine": "google_reverse_image",
                "api_key": SERPAPI_KEY,
                "image_url": link
            }
            # GET request for image_url
            response = requests.get("https://serpapi.com/search", params=params)
            print(f"SerpApi Status: {response.status_code}")
            print(f"SerpApi Content (preview): {response.text[:200]}")
        else:
            print("file.io returned success=False")
            print(data)
    else:
        print(f"file.io failed: {response.text}")

except Exception:
    traceback.print_exc()

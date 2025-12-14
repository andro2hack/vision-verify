import requests
import io

def test_file_io():
    print("Testing file.io upload...")
    # Create dummy image
    img_byte_arr = io.BytesIO(b"fakeimagecontent")
    files = {"file": ("test.png", img_byte_arr, "image/png")}
    
    try:
        response = requests.post("https://file.io", files=files)
        print(f"Status: {response.status_code}")
        try:
            safe_text = response.text[:500]
            print(f"Raw Text (Preview): '{safe_text}'")
        except:
            print(f"Raw Text (Hex): {response.content[:500].hex()}")
            
        print(f"Headers: {response.headers}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("JSON parsed successfully:", data)
            except Exception as e:
                print(f"JSON Parse Error: {e}")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_file_io()

import requests
import json
import pyautogui
import io
import base64

def generate_response():
    # API endpoint URL
    url = 'http://localhost:11434/api/generate'

    # Get screenshots
    image = pyautogui.screenshot().resize((495, 270))

    # Convert image to base64 string
    buf = io.BytesIO()
    image.save(buf, 'PNG')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Request data
    data = {
        "model": "llava:13b",
        "prompt": "What is in this picture?",
        "images": [image_base64],
        "stream": False
    }

    # Convert data to JSON format
    json_data = json.dumps(data)

    try:
        # Send POST request to API endpoint
        response = requests.post(url, data=json_data)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Response error: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

response = generate_response()
if response is not None:
    print(response['response'])
else:
    print("No response received")

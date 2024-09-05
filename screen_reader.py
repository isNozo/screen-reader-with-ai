import requests
import json
import pyautogui
import io
import base64

# Read API key
f = open("api_key", "r")
api_key = f.read()


def generate_response():
    # API endpoint URL
    url = "https://api.openai.com/v1/chat/completions"

    # Get screenshots
    image = pyautogui.screenshot().resize((495, 270))

    # Convert image to base64 string
    buf = io.BytesIO()
    image.save(buf, "PNG")
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    # Request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    # Request data
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    try:
        # Send POST request to API endpoint
        response = requests.post(url, headers=headers, json=data)

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
    print(json.dumps(response, indent=4))
else:
    print("No response received")

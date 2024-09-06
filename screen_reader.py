from openai import OpenAI
import pyautogui
import io
import base64

# Read API key
f = open("api_key", "r")
api_key = f.read()

# Init OpenAI
client = OpenAI(api_key=api_key)


def generate_response():
    # Get screenshots
    image = pyautogui.screenshot()

    # Convert image to base64 string
    buf = io.BytesIO()
    image.save(buf, "PNG")
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    # Send request to API endpoint
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {"image": image_base64, "resize": 768},
                ],
            }
        ],
        max_tokens=200,
    )

    return response


response = generate_response()
print(response.model_dump_json(indent=2))

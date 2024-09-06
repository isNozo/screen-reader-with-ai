from openai import OpenAI
import pyautogui
import io
import base64
import time

# Read API key
f = open("api_key", "r")
api_key = f.read()

# Init OpenAI
client = OpenAI(api_key=api_key)


# Get multiple screenshots
def get_screenshots():
    # Create a list to store the images
    images = []

    for i in range(10):
        # Get screenshots
        image = pyautogui.screenshot()

        # Convert image to base64 string
        buf = io.BytesIO()
        image.save(buf, "PNG")
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        images.append(image_base64)

        time.sleep(0.5)

    return images


def generate_response():
    # Get screenshots
    base64Frames = get_screenshots()

    # Send request to API endpoint
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "These are frames of a video. Create a short voiceover script in the style of David Attenborough. Only include the narration.",
                    },
                    *map(lambda x: {"image": x, "resize": 768}, base64Frames),
                ],
            }
        ],
        max_tokens=300,
    )

    return response


response = generate_response()
print(response.model_dump_json(indent=2))

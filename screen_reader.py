from openai import OpenAI
import pyautogui
import io
import base64
import time
from playsound import playsound

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
        print(f"Getting screenshot {i}...")
        image = pyautogui.screenshot().resize((480, 270))
        image.save(f"screenshot_{i}.png", "PNG")

        # Convert image to base64 string
        buf = io.BytesIO()
        image.save(buf, "PNG")
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        images.append(image_base64)

        time.sleep(0.5)

    return images


def generate_completion():
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
                        "text": "これはビデオのフレームです。解説者のスタイルで140文字の短いナレーション・スクリプトを作ってください。ナレーションだけを入れてください。",
                    },
                    *map(
                        lambda x: {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpg;base64,{x}",
                                "detail": "low",
                            },
                        },
                        base64Frames,
                    ),
                ],
            }
        ],
        max_tokens=300,
    )

    return response

while True:
    response = generate_completion()
    print(response.model_dump_json(indent=2))

    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=response.choices[0].message.content,
    ) as speech:
        speech.stream_to_file("output.mp3")

    playsound("output.mp3")

    time.sleep(30)

from openai import OpenAI
import pyautogui
import io
import base64
import time
import pyaudio

# Read API key
f = open("api_key", "r")
api_key = f.read()

# Init OpenAI
client = OpenAI(api_key=api_key)


# Get multiple screenshots
def get_screenshots():
    # Create a list to store the images
    images = []

    for i in range(8):
        # Get screenshots
        print(f"Getting screenshot {i}...")
        image = pyautogui.screenshot().resize((240, 135))
        image.save(f"screenshot_{i}.png", "PNG")

        # Convert image to base64 string
        buf = io.BytesIO()
        image.save(buf, "PNG")
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        images.append(image_base64)

        time.sleep(0.6)

    return images


message_history = []


def generate_completion():
    # Get screenshots
    base64Frames = get_screenshots()

    # Send request to API endpoint
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": "これまでの状況説明を出力してください。",
            },
            {"role": "assistant", "content": "\n".join(message_history)},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "これは現在の画面のフレームです。解説者として、次の場面を推測しながら状況を簡潔に短く200文字で説明してください。これまでの状況説明と同じような内容は出力しないでください。とくに文章の初めの表現が同じにならないように気を付けてください。",
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
            },
        ],
        max_tokens=300,
    )

    return response


def textToSpeech(text):
    player = pyaudio.PyAudio().open(
        format=pyaudio.paInt16, channels=1, rate=24000, output=True
    )

    print("request TTS api")

    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        response_format="pcm",
        input=text,
    ) as response:
        for chunk in response.iter_bytes(chunk_size=1024):
            player.write(chunk)

    print("speech end")

    return


while True:
    response = generate_completion()
    print(response.model_dump_json(indent=2))

    # Add message to history
    message = response.choices[0].message.content
    # Limit message_history to N messages
    if len(message_history) >= 3:
        # Remove oldest message from history
        del message_history[0]

    # Add new message to history
    message_history.append(message)

    print("\n".join(message_history))

    textToSpeech(response.choices[0].message.content)

    time.sleep(60)

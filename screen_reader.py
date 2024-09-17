from openai import OpenAI
import pyautogui
import io
import base64
import time
import pyaudio
import requests
import json

# Read API key
f = open("api_key", "r")
api_key = f.read()

# Init OpenAI
client = OpenAI(api_key=api_key)


# Get multiple screenshots
def get_screenshots():
    # Create a list to store the images
    images = []

    for i in range(4):
        # Get screenshots
        print(f"Getting screenshot {i}...")
        image = pyautogui.screenshot().resize((480, 270))
        image.save(f"screenshot_{i}.png", "PNG")

        # Convert image to base64 string
        buf = io.BytesIO()
        image.save(buf, "PNG")
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        images.append(image_base64)

        time.sleep(0.8)

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
                        "text": "これは現在の画面表示を録画した動画です。動画の内容について簡潔に短く200文字で説明してください。ただし、次の条件に従ってください。\n- 実況者と解説者の2人の掛け合いとして作ってください。\n- 出力フォーマットは次のようにしてください。\n**実況者:** [セリフ]\n**解説者:** [セリフ]\n- 画面に表示されている具体的なオブジェクトについて言及してください。",
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


def textToSpeech(text, voice):
    player = pyaudio.PyAudio().open(
        format=pyaudio.paInt16, channels=1, rate=24000, output=True
    )

    print("request TTS api")

    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=voice,
        response_format="pcm",
        input=text,
    ) as response:
        for chunk in response.iter_bytes(chunk_size=1024):
            player.write(chunk)

    print("speech end")

    return


def textToSpeech_local(text, voice):
    player = pyaudio.PyAudio().open(
        format=pyaudio.paInt16, channels=1, rate=24000, output=True
    )

    print("request TTS api")

    query = requests.post(
        f"http://127.0.0.1:50021/audio_query?text={text}&speaker={voice}"
    )

    synthesis = requests.post(
        f"http://127.0.0.1:50021/synthesis?speaker={voice}",
        headers={"Content-Type": "application/json"},
        data=json.dumps(query.json()),
    )

    player.write(synthesis.content)

    print("speech end")

    return


while True:
    response = generate_completion()
    print(response.model_dump_json(indent=2))

    # Add message to history
    message = response.choices[0].message.content
    # Limit message_history to N messages
    if len(message_history) >= 1:
        # Remove oldest message from history
        del message_history[0]

    # Add new message to history
    message_history.append(message)

    # split message by each line
    for line in message.splitlines():
        if line == "":
            continue

        print(line)

        # if the line contains a "実況者" or "解説者", then play each voice
        if "実況者" in line:
            line = line.replace("**実況者:**", "")
            textToSpeech_local(line, 3)
        elif "解説者" in line:
            line = line.replace("**解説者:**", "")
            textToSpeech_local(line, 13)

    time.sleep(60)

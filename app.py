import streamlit as st
import requests
import sounddevice as sd
import wavio
import openai
import os

os.environ["OPENAI_API_KEY"] = "API_KEY"
client = openai.OpenAI()

def get_audio_devices():
    devices = sd.query_devices()
    return devices

def record_audio(filename, duration, fs):
    try:
        print("Recording audio...")

        input_device = sd.default.device[0] 
        print(f"Using input device: {input_device}")

        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=input_device)
        sd.wait()

        wavio.write(filename, recording, fs, sampwidth=2)
        print("Audio recorded and saved as", filename)

    except Exception as e:
        print("Error:", e)
        print("Available devices:", get_audio_devices())  

st.title("🎤 Voice-to-Image Generator")
st.write("Click the button below to speak:")

if st.button(label="Click here to speak"):
    audio_filename = "input.wav"
    duration = 5  
    fs = 44100  

    record_audio(audio_filename, duration, fs)

    with open(audio_filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        a = transcript.text
        st.write("Transcribed Text:", a)

    response = client.images.generate(
        model="dall-e-2",
        prompt=a,
        size="1024x1024",
        quality="standard",
        n=1
    )

    image_url = response.data[0].url
    image_response = requests.get(image_url)

    image_path = "generated_image.jpg"
    with open(image_path, "wb") as f:
        f.write(image_response.content)
    print("Image generated and saved as", image_path)

    st.image(image_path)

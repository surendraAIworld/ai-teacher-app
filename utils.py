
def send_to_arduino(value, port='COM3', baudrate=9600):
    import serial, time
    try:
        arduino = serial.Serial(port, baudrate)
        time.sleep(2)
        arduino.write(value.encode())
        print(f"[SERIAL] Sent '{value}' to Arduino on {port}")
        arduino.close()
    except serial.SerialException as e:
        print(f"[SERIAL ERROR] Could not send to {port}: {e}")

import cohere
import os
import tempfile
from gtts import gTTS
import speech_recognition as sr


COHERE_API_KEY = "Ka3rd6ux3Anu6SAVta3BeVyDi0YDbjSlqrs8LrPj"
co = cohere.Client(COHERE_API_KEY)
current_audio_path = None

def generate_explanation(topic):
    prompt = f"You are an expert AI teacher. Simplify and explain the topic '{topic}' for grade 9 and 10 school students with clarity and examples. Avoid technical jargon."
    response = co.generate(model="command", prompt=prompt, max_tokens=600, temperature=0.7)
    return response.generations[0].text.strip()

def generate_answer(question):
    prompt = f"Answer this classroom question in 1-2 sentences for a school student: {question}"
    response = co.generate(model="command", prompt=prompt, max_tokens=100, temperature=0.5)
    return response.generations[0].text.strip()

def create_audio_file(text):
    global current_audio_path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts = gTTS(text=text, lang='en')
        tts.save(tmp_file.name)
        current_audio_path = tmp_file.name

def play_audio():
    if current_audio_path:
        pygame.mixer.music.load(current_audio_path)
        pygame.mixer.music.play()


def play_speech(text):
    create_audio_file(text)
    play_audio()
    import time
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def pause_speech():
    pygame.mixer.music.pause()

def resume_speech():
    pygame.mixer.music.unpause()

def stop_speech():
    global current_audio_path
    pygame.mixer.music.stop()
    if current_audio_path and os.path.exists(current_audio_path):
        try:
            os.remove(current_audio_path)
            current_audio_path = None
        except Exception as e:
            print(f"Error deleting temp file: {e}")

def listen_and_transcribe(timeout=15, phrase_time_limit=10, retries=3):
    recognizer = sr.Recognizer()
    attempt = 0
    while attempt < retries:
        with sr.Microphone() as source:
            print("🎤 Listening...")
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = recognizer.recognize_google(audio)
                print(f"🗣 You said: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                print("⌛ Timeout reached while waiting for speech.")
            except sr.UnknownValueError:
                print("❌ Could not understand audio.")
            except sr.RequestError as e:
                return f"Error with Google API: {e}"
        attempt += 1
    return ""

def generate_quiz(topic):
    return [
        {
            "question": f"What is the main idea of {topic}?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option A"
        },
        {
            "question": f"Why is {topic} important?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Option B"
        }
    ]

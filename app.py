
from streamlit_lottie import st_lottie
import json
import threading
import streamlit as st
import difflib
import time
from utils import generate_explanation, generate_answer, create_audio_file, play_audio, pause_speech, resume_speech, stop_speech, listen_and_transcribe, play_speech, send_to_arduino


def is_related(question, topic, threshold=0.05):
    import re
    question = question.lower().strip()
    topic = topic.lower().strip()
    topic_keywords = re.findall(r'\b\w+\b', topic)
    core_topic = topic_keywords[-1] if topic_keywords else topic
    return core_topic in question

with open("structure.json", "r") as f:
    data = json.load(f)

st.set_page_config(layout="centered", page_title="AI Teacher - DPS Nacharam")
st.markdown("""
    <style>
        .stApp { background-color: #0b1d3a; color: white; }
        h1, h2, h3 { color: #00FFAA; }
        .title-text { font-size: 36px; font-weight: bold; color: #00FFAA; text-align: center; }
        hr { border: 1px solid #00FFAA; }
        .stFileUploader, .stButton { display: none; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-text'>AI Teacher - DPS Nacharam</div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

if "status_message" not in st.session_state:
    st.session_state.status_message = ""

def handle_question(topic):
    while True:
        play_speech("Please ask your question.")
        question = listen_and_transcribe()
        if "stop" in question or question.strip() in ["no", "no thank you"]:
            play_speech("Thank you. Returning to home page.")
            return
        st.markdown(f"**Student asked:** {question}")
        related = is_related(question, topic)
        if related:
            answer = generate_answer(question)
        else:
            note = f"❌ This question is NOT related to the topic '{topic}'. Still, here's the answer."
            play_speech(note)
            st.markdown(f"**Notice:** {note}")
            answer = generate_answer(question)
        st.markdown(f"**AI Answer:** {answer}")
        create_audio_file(answer)
        send_to_arduino('1')
        play_audio()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        send_to_arduino('0')

def handle_explanation(topic):
    ai_output = generate_explanation(topic)
    st.markdown("### 🔍 AI Simplified Explanation")
    st.write(ai_output)
    create_audio_file(ai_output)
    send_to_arduino('1')
    play_audio()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    send_to_arduino('0')
    st.markdown("#### 🎧 Audio Controls")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⏸ Pause"):
            pause_speech()
    with col2:
        if st.button("▶️ Resume"):
            resume_speech()
    with col3:
        if st.button("⏹ Stop"):
            stop_speech()

def main_interaction():
    try:
        play_speech("Which subject do you want?")
        class_text = listen_and_transcribe()
        class_matches = difflib.get_close_matches(class_text, [c.lower() for c in data.keys()], n=1, cutoff=0.5)
        class_selection = next((c for c in data if c.lower() == class_matches[0]), None) if class_matches else None

        if not class_selection:
            st.error("subject not recognized.")
            play_speech("Sorry, subject not recognized.")
            return

        play_speech("Which chapter or unit do you want?")
        subject_text = listen_and_transcribe()
        subject_options = data[class_selection].keys()
        subject_matches = difflib.get_close_matches(subject_text, [s.lower() for s in subject_options], n=1, cutoff=0.5)
        subject_selection = next((s for s in subject_options if s.lower() == subject_matches[0]), None) if subject_matches else None

        if not subject_selection:
            st.error("chapter not recognized.")
            play_speech("Sorry, chapter not recognized.")
            return

        play_speech("Which topic do you want?")
        topic_text = listen_and_transcribe()
        topic_options = data[class_selection][subject_selection]
        topic_matches = difflib.get_close_matches(topic_text, [t.lower() for t in topic_options], n=1, cutoff=0.5)
        topic_selection = next((t for t in topic_options if t.lower() == topic_matches[0]), None) if topic_matches else None

        if not topic_selection:
            st.error("Topic not recognized.")
            play_speech("Sorry, topic not recognized.")
            return

        st.markdown(f"### ✅ You selected: {class_selection} → {subject_selection} → {topic_selection}")
        while True:
            play_speech("Your options are: Questions or Explanation. Please say your choice.")
            choice = listen_and_transcribe()

            if any(word in choice for word in ["1", "one", "question"]):
                handle_question(topic_selection)
            elif any(word in choice for word in ["2", "two", "explanation"]):
                handle_explanation(topic_selection)
                play_speech("Thank you. Returning to home page.")
                break
            elif "stop" in choice:
                play_speech("Okay, going back to home page.")
                break
            else:
                play_speech("Sorry, I didn't understand. Please say one or two.")
    except Exception as e:
        st.error(f"Interaction failed: {e}")

def wake_word_listener():
    welcome_msg = "Welcome to Delhi Public School. To interact with me, please call me the wake up word."
    play_speech(welcome_msg)
    st.session_state.status_message = welcome_msg

    while True:
        spoken = listen_and_transcribe()
        if "atom" in spoken:
            intro_msg = "I am an AI teacher from DPS"
            play_speech(intro_msg)
            st.session_state.status_message = intro_msg
            main_interaction()

# Launch listener in thread
threading.Thread(target=wake_word_listener, daemon=True).start()

# Display message placeholder
st.markdown(f'<p style="font-size:20px; text-align:center; color:#00FFAA;">{st.session_state.get("status_message", "")}</p>', unsafe_allow_html=True)

def load_lottiefile(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

st_lottie(load_lottiefile("robot.json"), speed=1, reverse=False, loop=True, quality="high", height=300)

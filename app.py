import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io
import os
import whisper
import difflib
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from audio_similarity import AudioSimilarity

# Get credentials from secrets.toml
USERNAME = st.secrets["passwords"]["username"]
PASSWORD = st.secrets["passwords"]["password"]
genai.configure(api_key=st.secrets["passwords"]["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

# Title and authentication
st.set_page_config(page_title="Welcome to English to German App", layout="centered")
st.write("")
st.write("")

st.header("Welcome to English to German Translator")
st.write("                                                ")
def login():
    st.subheader("Please log in to continue")
 
    u = st.text_input("Enter Username")
     
    p = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if u == USERNAME and p == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid credentials")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    login()
    st.stop()

# Main App Interface
# Translate
english_text = st.text_area("Enter English text to translate:")
if st.button("Translate"):
    if english_text.strip():
        prompt = f"Translate the following English text to German.avoid Suggestions:\n\n{english_text}"
        response = model.generate_content(prompt)
        german_translation = response.text.strip()
        st.session_state["german_translation"] = german_translation

        # Generate and store German audio
        tts = gTTS(german_translation, lang="de")
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        st.session_state["german_audio"] = audio_bytes.getvalue()

        # Save German audio
        original_path = "german_translation_audio.mp3"
        with open(original_path, "wb") as f:
            f.write(audio_bytes.getvalue())
        st.session_state["original_path"] = original_path
        # st.info(f"German translation audio saved to: {os.path.abspath(original_path)}")
    

# Show translation and audio
if "german_translation" in st.session_state:
    st.markdown("**German Translation:**")
    st.success(st.session_state["german_translation"])
    st.audio(st.session_state["german_audio"], format="audio/mp3")

# Record audio
duration = 5
sample_rate = 44100
if st.button("Start Recording"):
    st.info("Recording... Speak now!")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    st.success("Recording finished!")

    compare_path = "user_recording.wav"
    write(compare_path, sample_rate, recording)
    st.audio(compare_path, format="audio/wav")
    #st.success(f"Recording saved to: {os.path.abspath(compare_path)}")
    st.session_state["compare_path"] = compare_path

# # Upload audio
# uploaded_file = st.file_uploader("Or upload your German speech (WAV file)", type=["wav"])
# if uploaded_file is not None:
#     uploaded_path = "uploaded_user_recording.wav"
#     with open(uploaded_path, "wb") as f:
#         f.write(uploaded_file.read())
#     st.audio(uploaded_path, format="audio/wav")
#     st.success(f"Uploaded recording saved to: {os.path.abspath(uploaded_path)}")
#     st.session_state["compare_path"] = uploaded_path

# Transcribe and compare
if "german_translation" in st.session_state:
    file_to_compare = st.session_state.get("compare_path", None)
    original_path = st.session_state.get("original_path", None)

    if file_to_compare and os.path.exists(file_to_compare):
        st.info("Transcribing your speech...")
        model_whisper = whisper.load_model("base")
        result = model_whisper.transcribe(file_to_compare, language="de")
        user_spoken = result["text"].strip()
        st.markdown(f"**You said:** {user_spoken}")

        # Text comparison
        correct = st.session_state["german_translation"].lower()
        spoken = user_spoken.lower()
        seq = difflib.SequenceMatcher(None, correct, spoken)
        score = round(seq.ratio() * 100, 2)
        st.markdown(f"**Accuracy Score:** {score} / 100")

        # Audio similarity (optional)
        if original_path and os.path.exists(original_path):
            weights = {
                'zcr_similarity': 0.2,
                'rhythm_similarity': 0.2,
                'chroma_similarity': 0.2,
                'energy_envelope_similarity': 0.1,
                'spectral_contrast_similarity': 0.1,
                'perceptual_similarity': 0.2
            }
            audio_similarity = AudioSimilarity(original_path, file_to_compare, sample_rate, weights, verbose=True, sample_size=20)
            similarity_score = audio_similarity.stent_weighted_audio_similarity(metrics='all')
            st.markdown(f"**Similarity Score:** {similarity_score:.2f} / 1.00")
    else:
        st.warning("Please record.")
else:
    st.warning("Please translate some text first!")

# Logout button
if st.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

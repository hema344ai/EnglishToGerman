from gtts import gTTS
from pydub import AudioSegment

# Create MP3 from German text
tts = gTTS("Wie geht es dir?", lang='de')
tts.save("TEXT.mp3")

# Convert to WAV (requires ffmpeg installed)
audio = AudioSegment.from_mp3("TEXT.mp3")
audio.export("TEXT.wav", format="wav")
print("Saved 'TEXT.wav' successfully.")

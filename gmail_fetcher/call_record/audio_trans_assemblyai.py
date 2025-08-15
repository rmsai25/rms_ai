import time
import assemblyai as aai
from pymongo import MongoClient
from transformers import pipeline
from datetime import datetime
import sys
import os

# Add config path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.connection import connection
from get_llm_summary import summary

# === CONFIG ===
ASSEMBLYAI_API_KEY="Your api key"
AUDIO_FILE = 'wa_2mb_hindi.mpeg'  # Set your audio file here

# MongoDB setup
# client = connection()
db = connection()
collection = db["call_audio_data"]

# === Init AssemblyAI ===
aai.settings.api_key = ASSEMBLYAI_API_KEY
transcriber = aai.Transcriber()

# === Upload + Transcribe with Speaker Labels ===
print("🔄 Uploading & transcribing audio...")
try:
    transcript = transcriber.transcribe(
        AUDIO_FILE,
        config=aai.TranscriptionConfig(
            speaker_labels=True,
            speakers_expected=2,
            language='hi'
        )
    )
except Exception as e:
    print("❌ Transcription failed:", e)
    exit()

print("✅ Transcription complete.\n")

# === Speaker-separated Transcript ===
segments = transcript.utterances
print("🗣️ Speaker-separated Transcript:")
print("-" * 50)
output_lines = []

for segment in segments:
    line = f"Speaker {segment.speaker}: {segment.text}"
    print(line)
    output_lines.append(line)

joined_text = "\n".join(output_lines)

# === Summarize the Call ===
model_choice = input('Enter model: 1 for OpenAI summary, 2 for Hugging Face: ').strip()
summary_text = summary(model_choice, joined_text)

print("\n📌 Summary:")
print(summary_text)

# === Store in MongoDB ===
from_number = input("📞 Enter From number: ").strip()
to_number = input("📞 Enter To number: ").strip()

document = {
    "from_number": from_number,
    "to_number": to_number,
    "translated_text": joined_text,
    "summary_text": summary_text,
    "timestamp": datetime.utcnow(),
    "language": "en"  # You can later implement auto-detection
}

try:
    result = collection.insert_one(document)
    print(f"✅ Stored in MongoDB with ID: {result.inserted_id}")
except Exception as e:
    print("❌ MongoDB error:", e)

import os
import sys
from datetime import datetime
from pymongo import MongoClient
import anthropic

# Add project root for config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.connection import connection
from get_llm_summary import summary  # You already have this

# === CONFIG ===
AUDIO_FILE = "Enlish_sagarika.aac"  # 🎧 Path to your audio file
CLAUDE_API_KEY = os.environ.get("Your api key ")  # 🔐 Recommended to use env vars

# MongoDB
db = connection()
collection = db["call_audio_data"]

# === Transcribe with Claude ===
def transcribe_with_claude(audio_path):
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="claude-3-opus",
            prompt="""Transcribe the audio with speaker labels like 'Speaker A: Hello'. Maintain clear separation."""
        )
    return response.text

# === Main execution ===
if __name__ == "__main__":
    print("🔄 Transcribing audio with Claude AI...")
    try:
        transcript = transcribe_with_claude(AUDIO_FILE)
        print("✅ Transcription complete.\n")

        # Format speaker-separated output
        print("🗣️ Speaker-separated Transcript:")
        print("-" * 50)
        print(transcript)

        # === Generate Summary ===
        model_choice = input('Enter model: 1 for Claude Opus summary, 2 for Hugging Face: ').strip()
        summary_text = summary(model_choice, transcript)

        print("\n📌 Summary:")
        print(summary_text)

        # === Store in MongoDB ===
        from_number = input("📞 Enter From number: ").strip()
        to_number = input("📞 Enter To number: ").strip()

        document = {
            "from_number": from_number,
            "to_number": to_number,
            "transcript": transcript,
            "summary": summary_text,
            "timestamp": datetime.utcnow(),
            "language": "en"
        }

        result = collection.insert_one(document)
        print(f"✅ Stored in MongoDB with ID: {result.inserted_id}")

    except Exception as e:
        print(f"❌ Error: {e}")

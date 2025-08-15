import os
import sys
from datetime import datetime, timezone
import tempfile
import subprocess
import openai
from pymongo import MongoClient

# === Path setup ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.connection import connection
from get_llm_summary import summary

# === CONFIG ===
OPENAI_API_KEY = ""  # Replace with your actual key
AUDIO_FILE = "Eng_tenant_visit.mpeg" 
AUDIO_FILE="wa_2mb_hindi.mpeg" # Original AAC file
# LANGUAGE = "auto"
SUPPORTED_FORMATS = ['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm']

# === Setup OpenAI ===
openai.api_key = OPENAI_API_KEY

# === MongoDB connection ===
db = connection()
collection = db["call_audio_data"]

def convert_audio_to_wav(input_path):
    """Convert any audio file to WAV format using ffmpeg"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            output_path = temp_file.name
        
        # Convert using ffmpeg
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',  # Overwrite if exists
            output_path
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output_path
    
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg conversion failed: {e.stderr.decode()}")
        return None
    except Exception as e:
        print(f"❌ Conversion error: {str(e)}")
        return None

def transcribe_audio(audio_path):
    """Transcribe audio using OpenAI Whisper"""
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="verbose_json",
                prompt="""This is a real estate conversation. 
                Please transcribe clearly with proper punctuation.
                Important terms: BHK, sq ft, rent, deposit, furnished."""
            )
        return transcript
    except Exception as e:
        print(f"❌ Transcription failed: {str(e)}")
        return None

def process_transcript(transcript):
    """Add speaker labels using simple alternation"""
    # Access text attribute directly from the object
    text = transcript.text
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    # Simple speaker alternation (improve with diarization if needed)
    output = []
    for i, sentence in enumerate(sentences):
        speaker = "A" if i % 2 == 0 else "B"
        output.append(f"Speaker {speaker}: {sentence}.")
    
    return "\n".join(output)

def cleanup_temp_file(file_path):
    """Remove temporary converted file"""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"⚠️ Could not remove temp file: {str(e)}")

if __name__ == "__main__":
    print("🔄 Starting audio processing...")
    
    # 1. Check file exists
    if not os.path.exists(AUDIO_FILE):
        print(f"❌ File not found: {AUDIO_FILE}")
        exit(1)
    
    # 2. Convert if needed
    converted_file = None
    if not AUDIO_FILE.lower().endswith(tuple(SUPPORTED_FORMATS)):
        print("🔧 Converting audio to compatible format...")
        converted_file = convert_audio_to_wav(AUDIO_FILE)
        if not converted_file:
            exit(1)
        audio_to_transcribe = converted_file
    else:
        audio_to_transcribe = AUDIO_FILE
    
    # 3. Transcribe
    print("🔊 Transcribing audio...")
    transcript = transcribe_audio(audio_to_transcribe)
    if not transcript:
        cleanup_temp_file(converted_file)
        exit(1)
    
    # 4. Process transcript
    formatted_transcript = process_transcript(transcript)
    print("\n🗣️ Transcript:")
    print("-" * 50)
    print(formatted_transcript)
    
    # 5. Generate summary
    model_choice = input("\n📌 Choose summary model (1 for OpenAI, 2 for Hugging Face): ").strip()
    summary_text = summary(model_choice, formatted_transcript)
    
    print("\n📌 Summary:")
    print(summary_text)
    
    # 6. Store in MongoDB
    from_number = input("\n📞 Enter caller number: ").strip()
    to_number = input("📞 Enter recipient number: ").strip()
    
    document = {
        "from_number": from_number,
        "to_number": to_number,
        "transcript": formatted_transcript,
        "summary": summary_text,
        "timestamp": datetime.now(timezone.utc),
        "language": LANGUAGE,
        "original_file": AUDIO_FILE,
        "duration_seconds": transcript.duration,
        "word_count": len(transcript.text.split())
    }
    
    try:
        result = collection.insert_one(document)
        print(f"\n✅ Stored in MongoDB with ID: {result.inserted_id}")
    except Exception as e:
        print(f"❌ MongoDB error: {str(e)}")
    finally:
        cleanup_temp_file(converted_file)
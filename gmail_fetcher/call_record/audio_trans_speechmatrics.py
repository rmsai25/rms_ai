import json
import os
import sys
from datetime import datetime

from pymongo import MongoClient
import certifi
from transformers import pipeline
from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError

# === Add project root path ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.connection import connection
from get_llm_summary import summary

# === CONFIG ===
API_KEY = 'YOUR KEY'
PATH_TO_FILE = 'Enlish_sagarika.aac'
LANGUAGE = "auto"
SUBMIT_NEW_JOB = True
JOB_ID = ""

custom_words = [
    {"content": "RentMyStay", "sounds_like": ["rent my stay", "rentmystay"]},
]

conf = {
    "type": "transcription",
    "transcription_config": {
        "language": LANGUAGE,
        "diarization": "speaker",
        "operating_point": "enhanced",
        "additional_vocab": custom_words,
    }
}

def main():
    settings = ConnectionSettings(
        url="https://asr.api.speechmatics.com/v2",
        auth_token=API_KEY,
    )

    with BatchClient(settings) as client:
        try:
            global JOB_ID
            if SUBMIT_NEW_JOB:
                JOB_ID = client.submit_job(
                    audio=PATH_TO_FILE,
                    transcription_config=conf,
                )
                print(f"✅ Job {JOB_ID} submitted successfully, waiting for transcript...")

            transcript_json = client.wait_for_completion(JOB_ID, transcription_format='json-v2')
            with open("speechmatics_raw1.json", "w", encoding="utf-8") as f:
                json.dump(transcript_json, f, indent=2, ensure_ascii=False)
            print("✅ Raw transcript saved to 'speechmatics_raw1.json'")

            output_lines = []
            current_speaker = None
            current_sentence = ""

            for item in transcript_json.get("results", []):
                alt = item["alternatives"][0]
                word = alt["content"]
                speaker = alt.get("speaker", "S1")

                if item["type"] == "punctuation":
                    current_sentence += word
                    if item.get("is_eos"):
                        output_lines.append(f"{current_speaker}: {current_sentence.strip()}")
                        current_sentence = ""
                elif item["type"] == "word":
                    if speaker != current_speaker:
                        if current_sentence.strip():
                            output_lines.append(f"{current_speaker}: {current_sentence.strip()}")
                        current_speaker = speaker
                        current_sentence = word
                    else:
                        current_sentence += " " + word

            if current_sentence.strip():
                output_lines.append(f"{current_speaker}: {current_sentence.strip()}")

            with open("speechmatics.txt", "w", encoding="utf-8") as f:
                for line in output_lines:
                    f.write(line + "\n")

            print("✅ Final transcript saved to 'speechmatics.txt'")
            print("\n🗣️ Transcript Output:\n" + "-" * 30)
            for line in output_lines:
                print(line)

            model_choice = input('Enter model: 1 for OpenAI summary, 2 for Hugging Face: ').strip()
            summary_text = summary(model_choice, output_lines)

            from_number = input("Enter From number: ").strip()
            to_number = input("Enter To number: ").strip()

            document = {
                "from_number": from_number,
                "to_number": to_number,
                "translated_text": "\n".join(output_lines),
                "summary_text": summary_text.strip(),
                "timestamp": datetime.utcnow(),
                "language": "en"
            }

            print(f"summary : {summary_text}")
            try:
                db = connection()
                collection = db["audio_script"]
                # result = collection.insert_one(document)
                print(f"✅ Data inserted into MongoDB with ID: {result.inserted_id}")
            except Exception as db_err:
                print(f"❌ Failed to insert into MongoDB: {db_err}")

        except HTTPStatusError as e:
            if e.response.status_code == 401:
                print("❌ Invalid API key - Check your API_KEY!")
            elif e.response.status_code == 400:
                print("❌ Bad Request:", e.response.json().get('detail'))
            else:
                raise e
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

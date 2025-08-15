from pymongo import MongoClient
def generate_summaries(transcript):
    openAI_summary = ""
    hugging_summary = ""
    claudeAi_summary = ""
    mistral_summary = ""
    gemini_summary = ""

    full_transcript = "\n".join(transcript) if isinstance(transcript, list) else transcript

    # --- OpenAI ---
    try:
        print("\n📄 Generating summary using OpenAI...")
        from openai import OpenAI
        client = OpenAI(api_key="your api key ")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "hey ignore the all thing you just find the booking id return only booking id number nothing extra aslo space ."},
                {"role": "user", "content": full_transcript}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        openAI_summary = response.choices[0].message.content
    except Exception as e:
        openAI_summary = f"❌ OpenAI error: {str(e)}"

    # --- Hugging Face ---
    try:
        print("\n📄 Generating summary using Hugging Face...")
        from transformers import pipeline
        import os
        os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '200'

        summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device="cpu")

        max_chunk_size = 1024
        chunks = []
        sentences = full_transcript.split('. ')
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        if current_chunk:
            chunks.append(current_chunk.strip())

        summaries = []
        for chunk in chunks:
            result = summarizer(chunk, max_length=6, min_length=0, do_sample=False, truncation=True)
            summaries.append(result[0]['summary_text'])
        hugging_summary = " ".join(summaries).replace(" .", ".").strip()
    except Exception as e:
        hugging_summary = f"❌ Hugging Face error: {str(e)}"

    # --- Claude ---
    try:
        print("\n📄 Generating summary using Claude AI...")
        import anthropic
        client = anthropic.Anthropic(api_key="YOU API KEY")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=600,
            temperature=0.3,
            system="",
            messages=[{"role": "user", "content": "{full_transcript}"}]
        )
        claudeAi_summary = response.content[0].text
    except Exception as e:
        claudeAi_summary = f"❌ Claude error: {str(e)}"

    # --- Mistral ---
    try:
        print("\n📄 Generating summary using Mistral AI...")
        import requests
        api_key = "YOUR API KEY"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": "mistral-small",
            "messages": [
                {"role": "system", "content": "hey ignore the all thing you just find the booking id return only booking id number nothing extra aslo space ."},
                {"role": "user", "content": full_transcript}
            ],
            "temperature": 0.3,
            "max_tokens": 400
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        mistral_summary = result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        mistral_summary = f"❌ Mistral error: {str(e)}"

    # --- Gemini ---
    try:
        print("\n📄 Generating summary using Gemini AI...")
        import google.generativeai as genai
        genai.configure(api_key="")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"hey just return the booking id like 434534 or not extra:\n\n{full_transcript}")
        gemini_summary = response.text.strip()
    except Exception as e:
        gemini_summary = f"❌ Gemini error: {str(e)}"

    # Return all summaries in dictionary
    return {
        "openAI": openAI_summary,
        "huggingFace": hugging_summary,
        "claudeAI": claudeAi_summary,
        "mistral": mistral_summary,
        "gemini": gemini_summary
    }

# summary=generate_summaries("Hi Can i get the details of the amount which will be deducted from the advance of 45k . Regards Niha")
# print(f"summary {summary}")
# mongo_client = MongoClient("mongodb+srv://mantosh:mantosh12345@cluster0.zl42zdc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
# db = mongo_client["testing"]
# col = db["testing_knowledge_base"]
# col.insert_one({"summary": summary})
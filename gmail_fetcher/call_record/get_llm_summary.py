import os
def summary(model, transcript):
    # Ensure transcript is properly joined if it's a list
    if isinstance(transcript, list):
        full_transcript = "\n".join(transcript)
    else:
        full_transcript = transcript

    if model == "1":
        print("\n📄 Generating summary using OpenAI...")
        from openai import OpenAI  # Import the new OpenAI client

        # Initialize the client with your API key
        client = OpenAI(api_key="your api key ")  # Replace with your actual key
        
        prompt = """Please provide a detailed business summary (300-500 words) of this real estate conversation for RentMyStay.com in Bangalore.
        Correct any misheard words (like 'plant' to 'flat').
        Focus on key details: property type, requirements, pricing, and next steps.
        Conversation, i want to make sure give summary in same language as below transcript  like ( example transcript:in hinidi,then , summary_should: in hindi):\n""" + full_transcript
        print(f"prompt+script {prompt}")
        
        try:
            response = client.chat.completions.create( 
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a real estate conversation analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content  # Updated response access
        except Exception as e:
            return f"❌ OpenAI error: {str(e)}"

    elif model == "2":
        print("\n📄 Generating summary using Hugging Face...")
        from transformers import pipeline
        import os

        # Set longer timeout
        os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '600'
        
        prompt = """Summarize this real estate conversation focusing on:
        - Property requirements (type, furnishing)
        - Price range discussed
        - Contact details exchanged
        - Next steps planned\n\n"""
        
        full_text = prompt + full_transcript

        try:
            # Try with standard BART model
            summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device="cpu"  
            )
            
            max_chunk_size = 1024
            chunks = []
            sentences = full_text.split('. ')
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < max_chunk_size:
                    current_chunk += sentence + ". "
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            if current_chunk:
                chunks.append(current_chunk.strip())

            # Process each chunk
            summaries = []
            for chunk in chunks:
                result = summarizer(
                    chunk,
                    max_length=150,
                    min_length=50,
                    do_sample=False,
                    truncation=True
                )
                summaries.append(result[0]['summary_text'])
            print(f"hugging face : {summaries}")
            return " ".join(summaries).replace(" .", ".").strip()
        
        except Exception as e:
            return f"❌ Hugging Face error: {str(e)}"
    elif model == "3":
        print("\n📄 Generating summary using Claude AI...")
        import anthropic
        client = anthropic.Anthropic(api_key="your api key ")
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                temperature=0.3,
                system="You are a real estate call assistant. Summarize the call with key points, decisions, and next steps.",
                messages=[
                    {"role": "user", "content": f"Summarize this transcript:\n\n{full_transcript}"}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"❌ Claude error: {str(e)}"

    elif model == "4":
        print("\n📄 Generating summary using Mistral AI...")
        import requests

        api_key = ""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistral-small",
            "messages": [
                {"role": "system", "content": "You summarize real estate call transcripts."},
                {"role": "user", "content": f"Summarize the following call:\n\n{full_transcript}"}
            ],
            "temperature": 0.3,
            "max_tokens": 400
        }

        try:
            response = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data)
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"❌ Mistral error: {str(e)}"

    elif model == "5":
        print("\n📄 Generating summary using Gemini AI (Google)...")
        import google.generativeai as genai
        genai.configure(api_key="")
        try:
            # Use a supported model name like "gemini-1.0-pro-latest"
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                f"""Summarize this real estate call transcript with key topics, decisions, and any actions required:\n\n{full_transcript}"""
            )
            return response.text.strip()
        except Exception as e:
          return f"❌ Gemini error: {str(e)}"
    else:
        return "❌ Invalid model selected. Choose 1 for OpenAI, 2 for Hugging Face, 3 for Claude, 4 for Mistral, 5 for Gemini."
model=input("FOr SummaryEnter 1 for open ai \n 2 for hugging face \n 3 for claude ai \n 4 for mistral ai \n 5 for gemini ")
transcript="""S1: Yes, sir.
S1: Hello?
S1: Hello?
S1: Yes, sir.
S2: Yeah, so I got a call right now.
S1: Yes, sir.
S2: Yeah, I'm looking for one bc fully furnished.
S2: Uh, near Madhavpur or Bagmane tech Park one.
S2: Yeah, one BC if it's Semi-furnished, then also it is fine.
S1: Uh, so actually, we have only fully furnished.
S2: Yeah.
S2: That's fine.
S2: Yeah, you can tell me.
S1: Okay.
S1: So can I have your WhatsApp number?
S2: Yeah.
S2: Can you note it down?
S1: Yeah, yeah.
S2: 8808067671481486969.
S2: Yeah.
S2: What's in the range of one?
S2: Fully furnished.
S1: So starting from 27,000.
S2: Mhm.
S2: Yeah.
S2: You can share me.
S1: Yeah sure.
S1: I'll share you details on your WhatsApp sir.
S2: Okay.
S1: Before going for visit now sir.
S1: Call the caretaker.
S1: He will show you the flat.
S2: All right.
S1: Okay.
S1: And so you can check in our website also.
S2: Yeah.
S1: And we are not charging any brokerage.
S2: Okay.
S1: And sir, if you you can schedule the site visit.
S1: Also when you should do the site visit, you will get the caretaker number.
S2: Okay."""
trans=""" : Yes, sir.  : Hello?  : Hello?  : Yes, sir.  : Yeah, so I got a call right now.  : Yes, sir.  : Yeah, I'm looking for one bc fully furnished.  : Uh, near Madhavpur or Bagmane tech Park one.  : Yeah, one BC if it's Semi-furnished, then also it is fine.  : Uh, so actually, we have only fully furnished.  : Yeah.  : That's fine.  : Yeah, you can tell me.  : Okay.  : So can I have your WhatsApp number?  : Yeah.  : Can you note it down?  : Yeah, yeah.  : 8808067671481486969.  : Yeah.  : What's in the range of one?  : Fully furnished.  : So starting from 27,000.  : Mhm.  : Yeah.  : You can share me.  : Yeah sure.  : I'll share you details on your WhatsApp sir.  : Okay.  : Before going for visit now sir.  : Call the caretaker.  : He will show you the flat.  : All right.  : Okay.  : And so you can check in our website also.  : Yeah.  : And we are not charging any brokerage.  : Okay.  : And sir, if you you can schedule the site visit.  : Also when you should do the site visit, you will get the caretaker number.  : Okay."""
smry=summary(model, trans)
print("\n📌 Summary:")
print(smry)
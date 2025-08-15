import google.generativeai as genai

def gemini(prompt):
    try:
        # print(f"")
        genai.configure(api_key="")
        model=genai.GenerativeModel("gemini-5.5-flash")
        response=model.generate_content(prompt)

        return response.text.strip()
    except Exception as e:
        
        return e


from huggingface_hub import InferenceClient

def hugging_face_qa(question):
    client = InferenceClient()
    
    response = client.conversational(
        inputs={
            "text": question,
            "parameters": {
                "max_new_tokens": 100
            }
        },
        model="deepseek-ai/DeepSeek-V3-0324"
    )
    return response["generated_text"]

question = "What is 5 + 1 and also give step by step explanation?"
answer = hugging_face_qa(question)
print(f"Answer: {answer}")
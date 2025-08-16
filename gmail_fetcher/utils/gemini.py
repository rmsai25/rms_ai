import google.generativeai as genai
import os 
import sys
from load_env import load_env

# Pre-load keys when imported
# keys = load_env("GEMINI_KEY")
# print (f"key {keys}")

def gemini(prompt):
    try:
        # print(f"")
        genai.configure(api_key=f"{load_env("GEMINI_KEY")}")
        model=genai.GenerativeModel("gemini-1.5-flash")
        response=model.generate_content(prompt)

        return response.text.strip()
    except Exception as e:
        
        return e

# ans=gemini("hey give the top 2 news today ")
# print(f"answer  {ans}")

from huggingface_hub import InferenceClient

client = InferenceClient(api_key=f"{load_env("HUGGINGFACE_KEY")}")

def hugging_face_qa(question):
    completion = client.chat.completions.create(
        model="HuggingFaceH4/zephyr-7b-beta",   # ✅ use a supported chat model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ],
    )
    return completion.choices[0].message["content"]

question = "What is the capital of France?"
answer = gemini(question)
print(answer)
print(f"Answer: {answer}")
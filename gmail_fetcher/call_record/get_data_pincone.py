from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from transformers import pipeline


pc = Pinecone(api_key="your api key ")  
index = pc.Index(index_name)


embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def fetch_context_from_pinecone(query, top_k=3):
    query_embedding = embedding_model.encode(query).tolist()
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
   
    context = [match["metadata"]["content"] for match in results["matches"]]
    return context


qa_model = pipeline("text2text-generation", model="google/flan-t5-base")

def generate_answer(query, context):
    context_str = "\n".join(context)
    prompt = f"""Answer according to company policy:
    Question: {query}
    Context: {context_str}
    Answer:"""
    answer = qa_model(prompt, max_length=200)[0]["generated_text"]
    return answer.strip()
c
# Run the pipeline
query = input("Enter your query: ")
context = fetch_context_from_pinecone(query, 3)
print(f"context {context}")
answer = generate_answer(query, context)
print(f"Answer: {answer}")
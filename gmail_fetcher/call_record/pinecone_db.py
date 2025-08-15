from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import time

pc = Pinecone(api_key="your api key ")  
index_name = "techai"
dimension = 384 


existing_indexes = pc.list_indexes().names()
if index_name in existing_indexes:
    index_info = pc.describe_index(index_name)
    if index_info.dimension != dimension:
        print(f"⚠️ Deleting existing index with wrong dimension {index_info.dimension}...")
        pc.delete_index(index_name)
        time.sleep(10)  

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    time.sleep(1)  

index = pc.Index(index_name)
model = SentenceTransformer("all-MiniLM-L6-v2")

text = "compay allow 5 days leave in one month."
embedding = model.encode(text).tolist()


assert len(embedding) == dimension, f"Embedding dim {len(embedding)} != index dim {dimension}"

index.upsert([("doc-2", embedding, {"content": text})])
print("✅ Vector inserted successfully")

# try

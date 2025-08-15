import os
import sys
from sentence_transformers import SentenceTransformer


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from config.connection import connection
from utils.gemini import gemini
def getEmail():
  
    db = connection()
    # collection = db['email_data']
    collection=db['emails']
    embedder = SentenceTransformer('all-MiniLM-L6-v2')

  
    cursor = collection.find().limit(10)
    if cursor is None:
        print("null data")
    for doc in cursor:
        doc_id = doc.get("_id")

        summary = doc.get("body")
        summary=gemini(f"give proper summary {summary}")
        print("getting")
        if summary is None:
            print(f"[DEBUG] Document {doc_id} has no 'summary' field. Full doc: {doc}")
            continue  

        print(f"✅ \n summary for ID {doc_id}: {summary}")

        # Generate embedding
        vector = embedder.encode(summary).tolist()

        # Update document with embedding
        # result = collection.update_one(
        #     {"_id": doc_id},
        #     {"$set": {"embedding": vector}}
        # )

        # print(f"🔄 Updated embedding for ID {doc_id}, Matched: {result.matched_count}, Modified: {result.modified_count}")

# if __name__ == "__main__":
getEmail()

from pymongo import MongoClient
import certifi

def connection():
    MONGO_URI = "your uri "
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client["gmail_data"] 
    # db=client["gmail"]
    return db

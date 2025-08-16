from pymongo import MongoClient
import certifi
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.load_env import load_env
def connection():
    MONGO_URI = f"{load_env("MONGO_URI")}"
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client["gmail"] 
    return db

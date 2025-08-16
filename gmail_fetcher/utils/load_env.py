# utils/config_loader.py
from pathlib import Path
from dotenv import load_dotenv
import os

def load_env(name_api_key):
    env_path = Path(__file__).parent / ".env"  
    load_dotenv(env_path)  
    
    return os.getenv(name_api_key)

# # Pre-load keys when imported
# keys = load_env("GEMINI_KEY")
# print (f"key {keys}")

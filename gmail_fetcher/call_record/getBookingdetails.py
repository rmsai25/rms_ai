import os
import sys
import json
import requests
from pymongo import MongoClient 
# import jsonify

# Access parent directory for config import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.connection import connection
import fetch_mail
from utils.gemini import gemini


def fetch_booking_details():
    db = connection()
    collection = db["emails"]

    # Authenticate and fetch emails
    service = fetch_mail.gmail_authenticate()
    query = "from:(kiran@rentmystay.com) subject:(test email) is:important after:2025/8/4 before:2025/8/7"
    emails = fetch_mail.get_emails(service, query)

    print(f"\n✅ Emails:\n{json.dumps(emails, indent=2)}")

    if not emails:
        print("❌ No emails found.")
        return

    # Extract first email body
    email_body = emails[0].get("body", "")
    print(f"\n📩 First Email Body:\n{email_body}")
    msgid=emails[0].get("msgid","")
    res=collection.find({"thread_id":"1986423fb3fb42c1"})
    emails_data=[]
    print("email fetch from mowngodb ")
    for doc in res:
       doc["_id"]=str(doc["_id"])
       emails_data.append(doc)
    
    print(json.dumps(emails_data, indent=4))
    # exit()

    try:
        print("\n📄 Generating summary using Gemini AI...")
        # import google.generativeai as genai

        # genai.configure(api_key="AIzaSyAFJ5E9N38fruKGnde2kYq6GANYmc9S3dw")
        # model = genai.GenerativeModel("gemini-1.5-flash")
        prompt=f"Extract only the booking ID from the following email:\n\n{email_body}"
        response=gemini(prompt)
        # booking_id = gemini_response.text.strip()
        print(f"📦 Extracted Booking ID: {response}")
        booking_id=response


        # print
        # exit()
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return

    # Booking Search API
    url = "https://www.rentmystay.com/A2/bookingSearch"
    params = {
        "email": "your mail@gmail.com",
        "phonenumber": "sds",
        "booking_id": booking_id
    }
    headers = {
        "Authorization": "your authentication code "
    }
    try:
        booking_response = requests.get(url, params=params, headers=headers)
        print(f"🌐 API Status Code: {booking_response.status_code}")
        data = json.dumps(booking_response.json(), indent=2) + "\n\n" + json.dumps(emails, indent=2)

        
        # print(f"\n📋 Booking Details:\n")
        client = db["call_audio_data"]
        data_response=client.find({},{"translated_text": 1})
        text_tranlate=[]
        for doc in data_response:
            # print(doc["translated_text"])
            text_tranlate.append(doc["translated_text"])
        # exit()
        data=data+"\n\n"+json.dumps(text_tranlate, indent=2)
        prompt=f"what is the rent of this booking , and what is the tenant name and what is the tenant query ,and how nay ticket he raised, also give the best summary collectively, in json format   {data}"
        answer=gemini(prompt)
        print(answer)

    except ValueError:
        print("❌ Error parsing booking API response.")
    except Exception as e:
        print(f"❌ Request failed: {e}")
        
fetch_booking_details()

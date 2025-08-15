from google.oauth2.credentials import Credentials 
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pytz import timezone
import base64
import os
import re
from datetime import datetime, timedelta, timezone as dt_timezone
from config.connection import connection

# === CONFIG ===
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

db = connection()
connection = db["emails"]

def gmail_authenticate():
    creds = None
    if os.path.exists('gmailtoken.json'):
        creds = Credentials.from_authorized_user_file('gmailtoken.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('gmailtoken.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def decode_base64(data):
    return base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8', errors='ignore')

def clean_text(raw_text):
    soup = BeautifulSoup(raw_text, "html.parser")
    text = soup.get_text()
    text = re.sub(r'[^\x20-\x7E]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_email_body(payload):
    if payload.get('parts'):
        for part in payload['parts']:
            mime_type = part.get('mimeType', '')
            data = part['body'].get('data')
            if data:
                content = decode_base64(data)
                return clean_text(content)
    else:
        data = payload['body'].get('data')
        if data:
            content = decode_base64(data)
            return clean_text(content)
    return "(No readable content found)"

def get_emails(service, query=""):
    emails = []
    page_token = None
    
    while True:
        results = service.users().messages().list(
            userId='me',
            q=query,
            pageToken=page_token,
            maxResults=500  
        ).execute()
        
        messages = results.get('messages', [])
        print(f"📨 Found {len(messages)} message(s) in this batch.")
        
        for msg in messages:
            try:
                msg_data = service.users().messages().get(
                    userId='me', 
                    id=msg['id'], 
                    format='full'
                ).execute()
                
                payload = msg_data.get('payload', {})
                headers = payload.get('headers', [])

                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                raw_sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')
                match = re.search(r'<([^>]+)>', raw_sender)
                sender = match.group(1) if match else raw_sender
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '(No Date)')

                try:
                    date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S %Z')
                except Exception:
                    formatted_date = date_str

                body = extract_email_body(payload)
                snippet = msg_data.get('snippet', '')[:200]
                msgid = msg_data.get('id')
                thread_id = msg_data.get('threadId')

                emails.append({
                    "subject": subject,
                    "sender": sender,
                    "date": formatted_date,
                    "body": body,
                    "snippet": snippet,
                    "msgid": msgid,
                    "thread_id": thread_id,
                    
                })
            except Exception as e:
                print(f"Error processing message {msg['id']}: {str(e)}")
                continue
        
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    print(f"📨 Total messages found: {len(emails)}")
    return emails

# === MAIN EXECUTION === 
if __name__ == '__main__':
    service = gmail_authenticate()

    utc_now = datetime.now(dt_timezone.utc)
    ist = timezone('Asia/Kolkata')
    now_ist = utc_now.astimezone(ist)
    one_day_ago_ist = now_ist - timedelta(days=24)
    thirty_days_ago_ist = now_ist - timedelta(days=5)

    after_timestamp = int(thirty_days_ago_ist.timestamp())
    before_timestamp = int(now_ist.timestamp())

    print("🕒 Fetching emails from:", thirty_days_ago_ist.strftime('%Y-%m-%d %H:%M:%S'), "to", now_ist.strftime('%Y-%m-%d %H:%M:%S'))

    query = f"after:{after_timestamp} before:{before_timestamp} (in:inbox OR in:sent)"
    emails = get_emails(service, query=query )

    for email in emails:
        print(f"\n--- {email['subject']} from {email['sender']} on {email['date']}")
        print(f"Snippet: {email['snippet']}")
        print(f"Body: {email['body'][:200]}...\n")
        connection.insert_one(email)

    print(f"✅ {len(emails)} email(s) saved to MongoDB.")

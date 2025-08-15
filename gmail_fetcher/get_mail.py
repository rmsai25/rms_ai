from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from config.connection import connection

app = Flask(__name__)
CORS(app)  
db=connection()
collection = db["emails"]
@app.route('/get_mail_by_sender/<sender>', methods=['GET'])
def get_emails_by_sender(sender):
    documents = collection.find({"sender":sender})
    emails = []
    for doc in documents:   
        doc['_id'] = str(doc['_id   v'])  
        emails.append(doc)
    return jsonify(emails)

@app.route('/get_emails/emails', methods=['GET'])
def get_emails():
    documents = collection.find()
    emails = []
    for doc in documents:   
        doc['_id'] = str(doc['_id'])  
        emails.append(doc)
    return jsonify(emails)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

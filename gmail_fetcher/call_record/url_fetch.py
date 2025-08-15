import requests 

url="http://localhost:5000/get_emails/emails"
response=requests.get(url)
if response.status_code==200:
    print(f"response data {response.json()}")
else:
    print(response.status_code)
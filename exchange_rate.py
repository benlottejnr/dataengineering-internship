import os
import requests
import json
from datetime import datetime
from google.cloud import storage

API_KEY = "d4d1547e423242e2d0f3f8c3" #api key for currency conversion
url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
response = requests.get(url)
data = response.json()

if response.status_code == 200 and data["result"] == "success":
    today = datetime.now().strftime('%Y-%m-%d') #getting today's date so I use it for partitioning

    client = storage.Client() #initializing gcs client
    bucket_name = 'storypointsai_client1' #bucket name to hold info
    bucket = client.bucket(bucket_name)

    #defining path for data storage
    blob_path = f"data/raw/api_currency/{today}/exchange_rates.json"
    blob = bucket.blob(blob_path)

    #upload
    blob.upload_from_string(
        data=json.dumps(data, indent=2),
        content_type='application/json'
    )
    
    print(f"Successfully uploaded to gs://{bucket_name}/{blob_path}")
else:
    print("API Error:", data)
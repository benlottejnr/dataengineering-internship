import os
import requests
API_KEY = "d4d1547e423242e2d0f3f8c3" # Replace with your key
url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
response = requests.get(url)
data = response.json()
if response.status_code == 200 and data["result"] == "success":
    rates = data["conversion_rates"]
    print("USD to INR:", rates["INR"])
else:
    print("API Error:", data)
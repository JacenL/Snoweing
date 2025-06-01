import requests
import json
import os

apiKey = os.getenv("hypixelAPIKeyDev")
ahURL = "https://api.hypixel.net/skyblock/auctions"

def fetch_all_auctions():
    all_auctions = []
    page = 0

    response = requests.get(ahURL, params={"key": apiKey, "page": page})
    data = response.json()
    total_pages = data["totalPages"]
    
    while page < total_pages:
        page += 1
        response = requests.get(ahURL, params={"key": apiKey, "page": page})
        print(f"Getting page {page} of {total_pages}")
        data = response.json()
        all_auctions.extend(data["auctions"])
    return all_auctions


auctions = fetch_all_auctions()
print(json.dumps(auctions, indent=4))

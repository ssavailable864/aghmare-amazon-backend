import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Tumhari Vercel website ko server se data lene ki permission dena
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://waghmare-pdf-sort-website.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Amazon Keys (Render ke andar se uthayega, code me khuli nahi dikhengi)
AMAZON_REFRESH_TOKEN = os.getenv("AMAZON_REFRESH_TOKEN")
AMAZON_CLIENT_ID = os.getenv("AMAZON_CLIENT_ID")
AMAZON_CLIENT_SECRET = os.getenv("AMAZON_CLIENT_SECRET")

def get_amazon_access_token():
    url = "https://api.amazon.com/auth/o2/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": AMAZON_REFRESH_TOKEN,
        "client_id": AMAZON_CLIENT_ID,
        "client_secret": AMAZON_CLIENT_SECRET
    }
    try:
        response = requests.post(url, data=payload)
        return response.json().get("access_token")
    except Exception as e:
        print("Token Error:", e)
        return None

@app.get("/")
def home():
    return {"status": "Waghmare Backend Live", "message": "Makkhan chal raha hai!"}

@app.get("/api/amazon-orders")
def get_today_orders_count():
    try:
        access_token = get_amazon_access_token()
        if not access_token:
            return {"status": "error", "message": "Amazon Token Failed"}

        # Europe/India SP-API Endpoint
        url = "https://sellingpartnerapi-eu.amazon.com/orders/v0/orders"
        headers = {
            "X-Amz-Access-Token": access_token,
            "Content-Type": "application/json"
        }

        # India Marketplace ID: A2196NY6051783
        params = {
            "MarketplaceIds": "A2196NY6051783",
            "CreatedAfter": "2026-05-25T00:00:00Z", # Baad mein isko automatic aaj ki date par set kar denge
            "MaxResultsPerPage": 100
        }

        response = requests.get(url, headers=headers, params=params)
        orders_data = response.json()

        orders_list = orders_data.get("payload", {}).get("Orders", [])
        total_orders = len(orders_list)

        return {"status": "success", "total_today": total_orders}

    except Exception as e:
        return {"status": "error", "message": str(e)}
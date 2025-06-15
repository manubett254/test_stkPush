from flask import Flask, render_template, request, jsonify
import requests
import base64
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Get env variables
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
shortcode = os.getenv("SHORTCODE")
passkey = os.getenv("PASSKEY")
callback_url = os.getenv("CALLBACK_URL")

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    return response.json().get("access_token")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        phone = request.form["phone"]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

        headers = {
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json"
        }

        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": 1,
            "PartyA": phone,
            "PartyB": shortcode,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "AccountReference": "Test123",
            "TransactionDesc": "Test Payment"
        }

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers
        )

        return jsonify(response.json())

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, jsonify
import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Try the default CORS setup

# Load environment variables
load_dotenv()

# Fetch credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

# Validate credentials
if not account_sid or not auth_token or not twilio_number:
    print("Error: Twilio credentials are missing!")
    sys.exit(1)

client = Client(account_sid, auth_token)

def initiate_call(to_number):
    try:
        call = client.calls.create(
            to=to_number,
            from_=twilio_number,
            url="https://258d-115-241-73-226.ngrok-free.app/voice"  # Use your current ngrok URL
        )
        print(f"Call initiated! SID: {call.sid}")
        return jsonify({"message": "Call initiated!", "sid": call.sid})
    except Exception as e:
        print(f"Error initiating call: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/make_call", methods=["POST"])
def make_call_api():
    data = request.json
    to_number = data.get("to_number")

    if not to_number:
        return jsonify({"error": "Phone number is required"}), 400

    return initiate_call(to_number)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
import os
import sys
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

# Fetch credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

# Check if credentials are loading
if not account_sid or not auth_token:
    print("Error: Twilio credentials are missing!")
    sys.exit(1)

client = Client(account_sid, auth_token)

def make_call(to_number):
    call = client.calls.create(
        to=to_number,
        from_=twilio_number,
        url="https://258d-115-241-73-226.ngrok-free.app/voice"  # Use your ngrok URL
    )
    print(f"Call initiated! SID: {call.sid}")

if __name__ == "__main__":
    # Directly call the specified number
    make_call("+919717700542")
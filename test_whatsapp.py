from twilio.rest import Client
import os

# Read Twilio credentials from environment variables to avoid leaking secrets
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    print("Twilio credentials not set in environment; aborting test.")
else:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # Put your exact real phone number here (no spaces, just the 10 digits)
    my_number = os.getenv("TEST_PHONE_NUMBER", "7676348202")

    print(f"Attempting to send direct message to: +91 {my_number}...")

    try:
        message = client.messages.create(
            from_="whatsapp:+14155238886",
            body="🚀 This is a Twilio test message from the SportsSaaS project.",
            to=f"whatsapp:+91{my_number}"
        )
        print(f"\n[SUCCESS] Message pushed to Twilio! ID: {message.sid}")
    except Exception as e:
        print(f"\n[TWILIO REJECTED THE MESSAGE]")
        print(f"Exact Error Reason: {e}")
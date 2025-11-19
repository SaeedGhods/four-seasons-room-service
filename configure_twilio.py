"""
Script to configure Twilio webhooks for the Four Seasons Room Service Agent
Run this after you have your Render URL
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def configure_twilio_webhooks(render_url):
    """Configure Twilio webhooks to point to Render"""
    
    if not all([ACCOUNT_SID, AUTH_TOKEN, PHONE_NUMBER]):
        print("❌ Error: Twilio credentials not found in .env file")
        print("Please make sure .env has:")
        print("  TWILIO_ACCOUNT_SID=...")
        print("  TWILIO_AUTH_TOKEN=...")
        print("  TWILIO_PHONE_NUMBER=...")
        return False
    
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        # Get the phone number
        phone_number = client.incoming_phone_numbers.list(phone_number=PHONE_NUMBER)
        
        if not phone_number:
            print(f"❌ Error: Phone number {PHONE_NUMBER} not found in your Twilio account")
            return False
        
        phone_sid = phone_number[0].sid
        
        # Update webhook URLs
        voice_url = f"{render_url}/voice"
        status_url = f"{render_url}/status"
        
        print(f"📞 Configuring Twilio phone number: {PHONE_NUMBER}")
        print(f"🔗 Voice webhook: {voice_url}")
        print(f"📊 Status webhook: {status_url}")
        
        client.incoming_phone_numbers(phone_sid).update(
            voice_url=voice_url,
            voice_method='POST',
            status_callback=status_url,
            status_callback_method='POST'
        )
        
        print("✅ Twilio webhooks configured successfully!")
        print(f"\n🎉 Setup complete! Call {PHONE_NUMBER} to test your agent.")
        return True
        
    except Exception as e:
        print(f"❌ Error configuring Twilio: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python configure_twilio.py <RENDER_URL>")
        print("Example: python configure_twilio.py https://four-seasons-room-service.onrender.com")
        sys.exit(1)
    
    render_url = sys.argv[1].rstrip('/')
    configure_twilio_webhooks(render_url)


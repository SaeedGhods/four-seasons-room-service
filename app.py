"""
Flask application for Four Seasons Room Service Phone Agent
Handles Twilio webhooks for incoming calls
"""

from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import os
from dotenv import load_dotenv
from agent import RoomServiceAgent

load_dotenv()

app = Flask(__name__)
agent = RoomServiceAgent()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return "Four Seasons Room Service Agent is running!", 200


@app.route("/voice", methods=["POST"])
def handle_incoming_call():
    """
    Handle incoming phone call
    Twilio will POST to this endpoint when a call comes in
    """
    call_sid = request.form.get("CallSid")
    
    response = VoiceResponse()
    
    # Initial greeting
    response.say(
        "Hello! Welcome to Four Seasons Toronto room service. "
        "I'm your virtual assistant, and I'm here to help you with our menu and take your order. "
        "Please speak naturally, and I'll assist you. How can I help you today?",
        voice="alice",
        language="en-US"
    )
    
    # Gather user input
    gather = Gather(
        input="speech",
        action="/process-speech",
        method="POST",
        speech_timeout="auto",
        language="en-US",
        hints="menu, order, price, burger, salad, pasta, dessert, chicken, salmon, beef"
    )
    response.append(gather)
    
    # Fallback if no input
    response.say(
        "I didn't catch that. Please tell me how I can help you with our menu.",
        voice="alice"
    )
    response.redirect("/voice")
    
    return str(response), 200, {"Content-Type": "text/xml"}


@app.route("/process-speech", methods=["POST"])
def process_speech():
    """
    Process speech input from user
    Twilio sends the transcribed speech here
    """
    call_sid = request.form.get("CallSid")
    speech_result = request.form.get("SpeechResult", "").strip()
    
    if not speech_result:
        response = VoiceResponse()
        response.say("I didn't catch that. Could you please repeat?", voice="alice")
        gather = Gather(
            input="speech",
            action="/process-speech",
            method="POST",
            speech_timeout="auto",
            language="en-US"
        )
        response.append(gather)
        return str(response), 200, {"Content-Type": "text/xml"}
    
    # Process with agent
    agent_response = agent.process_message(call_sid, speech_result)
    
    # Create TwiML response
    response = VoiceResponse()
    response.say(agent_response, voice="alice", language="en-US")
    
    # Continue conversation
    gather = Gather(
        input="speech",
        action="/process-speech",
        method="POST",
        speech_timeout="auto",
        language="en-US",
        hints="menu, order, price, burger, salad, pasta, dessert, chicken, salmon, beef, yes, no, add, remove, review, checkout"
    )
    response.append(gather)
    
    # Fallback
    response.say("Is there anything else I can help you with?", voice="alice")
    response.redirect("/process-speech")
    
    return str(response), 200, {"Content-Type": "text/xml"}


@app.route("/status", methods=["POST"])
def call_status():
    """Handle call status updates"""
    call_sid = request.form.get("CallSid")
    call_status = request.form.get("CallStatus")
    
    # Clean up conversation history when call ends
    if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
        if hasattr(agent, 'conversation_history') and call_sid in agent.conversation_history:
            del agent.conversation_history[call_sid]
        if hasattr(agent, 'active_orders') and call_sid in agent.active_orders:
            del agent.active_orders[call_sid]
    
    return "", 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)



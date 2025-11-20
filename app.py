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

# Store detected language per call
call_languages = {}

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return "Four Seasons Room Service Agent is running!", 200


def get_voice_for_language(lang_code):
    """Get appropriate Twilio voice for language"""
    voice_map = {
        "en-US": "alice", "en-GB": "alice", "en-AU": "alice", "en-CA": "alice",
        "es-ES": "Conchita", "es-MX": "Conchita", "es-US": "Conchita",
        "fr-FR": "Mathieu", "fr-CA": "Mathieu",
        "de-DE": "Hans",
        "it-IT": "Carla",
        "pt-BR": "Vitoria", "pt-PT": "Cristiano",
        "ja-JP": "Takumi",
        "ko-KR": "Seoyeon",
        "zh-CN": "Zhiyu", "zh-TW": "Zhiyu",
        "ar-SA": "Zeina", "ar-EG": "Zeina",
        "fa-IR": "Zira",  # Farsi/Persian
        "hi-IN": "Aditi",
        "ru-RU": "Tatyana",
        "nl-NL": "Lotte",
        "pl-PL": "Ewa",
        "tr-TR": "Filiz",
        "sv-SE": "Astrid",
        "da-DK": "Naja",
        "no-NO": "Liv",
        "fi-FI": "Suvi",
        "cs-CZ": "Josef",
        "hu-HU": "Gyorgy",
        "ro-RO": "Carmen",
        "th-TH": "Kanya",
        "vi-VN": "Linh"
    }
    # Default to alice for English if language not found
    return voice_map.get(lang_code, "alice")

@app.route("/voice", methods=["POST"])
def handle_incoming_call():
    """
    Handle incoming phone call
    Twilio will POST to this endpoint when a call comes in
    """
    call_sid = request.form.get("CallSid")
    
    # Default to English, but will detect from user's speech
    default_lang = "en-US"
    call_languages[call_sid] = default_lang
    
    response = VoiceResponse()
    
    # Initial greeting in multiple languages
    greetings = {
        "en-US": "Greetings from the Four Seasons. This is Nasrin, your dedicated room service concierge. How may I elevate your experience with a delightful dining moment today?",
        "es-ES": "Saludos desde Four Seasons. Soy Nasrin, su conserje dedicada de servicio a la habitación. ¿Cómo puedo elevar su experiencia con un momento gastronómico delicioso hoy?",
        "fr-FR": "Salutations du Four Seasons. Je suis Nasrin, votre concierge dédiée au service en chambre. Comment puis-je rehausser votre expérience avec un moment de dégustation délicieux aujourd'hui?",
        "de-DE": "Grüße vom Four Seasons. Ich bin Nasrin, Ihre persönliche Concierge für den Zimmerservice. Wie kann ich Ihr Erlebnis heute mit einem köstlichen kulinarischen Moment bereichern?",
        "it-IT": "Saluti dal Four Seasons. Sono Nasrin, la vostra concierge dedicata al servizio in camera. Come posso elevare la vostra esperienza con un delizioso momento gastronomico oggi?",
        "ja-JP": "フォーシーズンズよりご挨拶申し上げます。ルームサービスの専属コンシェルジュ、ナスリンでございます。本日、素晴らしい食事のひとときでお客様の体験をより豊かにするには、どのようにお手伝いできるでしょうか？",
        "zh-CN": "来自四季酒店的问候。我是纳斯林，您专属的客房服务礼宾。今天，我如何通过美妙的用餐时刻来提升您的体验？",
        "ar-SA": "تحيات من فور سيزونز. أنا نسرين، كونسيرج خدمة الغرف المخصصة لك. كيف يمكنني رفع تجربتك مع لحظة طعام لذيذة اليوم؟",
        "fa-IR": "درود از فور سیزونز. من نسرین هستم، کونسیرژ اختصاصی سرویس اتاق شما. امروز چگونه می‌توانم تجربه شما را با یک لحظه لذیذ غذایی ارتقا دهم؟",
        "hi-IN": "फोर सीज़न्स से अभिवादन। मैं नसरीन हूं, आपकी समर्पित रूम सर्विस कॉन्सिएर्ज। आज मैं एक स्वादिष्ट भोजन के क्षण के साथ आपके अनुभव को कैसे बढ़ा सकती हूं?",
        "ru-RU": "Приветствие от Four Seasons. Я Насрин, ваш персональный консьерж службы номеров. Как я могу улучшить ваше впечатление сегодня с помощью восхитительного кулинарного момента?",
        "pt-BR": "Saudações do Four Seasons. Sou Nasrin, sua concierge dedicada de serviço de quarto. Como posso elevar sua experiência com um momento gastronômico delicioso hoje?",
    }
    
    # Start with English greeting, but support all languages
    response.say(
        greetings.get(default_lang, greetings["en-US"]),
        voice=get_voice_for_language(default_lang),
        language=default_lang
    )
    
    # Gather user input - support multiple languages
    # Twilio will auto-detect language, but we can specify multiple
    gather = Gather(
        input="speech",
        action="/process-speech",
        method="POST",
        speech_timeout="auto",
        language="auto",  # Auto-detect language
        hints="menu, order, price, burger, salad, pasta, dessert, chicken, salmon, beef, menú, orden, precio, menù, ordine, prezzo, メニュー, 注文, 価格, 菜单, 订单, 价格, قائمة, طلب, سعر, منو, سفارش, قیمت"
    )
    response.append(gather)
    
    # Fallback if no input
    response.say(
        "I didn't catch that. Please tell me how I can help you with our menu.",
        voice=get_voice_for_language(default_lang),
        language=default_lang
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
    
    # Detect language from Twilio (if available) or use stored/default
    detected_lang = request.form.get("SpeechLanguage", None)
    if detected_lang:
        call_languages[call_sid] = detected_lang
        print(f"Detected language for call {call_sid}: {detected_lang}")
    
    # Use stored language or default to English
    current_lang = call_languages.get(call_sid, "en-US")
    voice = get_voice_for_language(current_lang)
    
    if not speech_result:
        response = VoiceResponse()
        fallback_messages = {
            "en-US": "I didn't catch that. Could you please repeat?",
            "es-ES": "No entendí eso. ¿Podría repetir, por favor?",
            "fr-FR": "Je n'ai pas compris. Pourriez-vous répéter, s'il vous plaît?",
            "de-DE": "Das habe ich nicht verstanden. Könnten Sie das bitte wiederholen?",
            "it-IT": "Non ho capito. Potresti ripetere, per favore?",
            "ja-JP": "聞き取れませんでした。もう一度言っていただけますか？",
            "zh-CN": "我没听清楚。请您再说一遍好吗？",
            "ar-SA": "لم أفهم ذلك. هل يمكنك التكرار من فضلك؟",
            "fa-IR": "متوجه نشدم. لطفاً دوباره بگویید؟",
            "hi-IN": "मैं समझ नहीं पाया। क्या आप कृपया दोहरा सकते हैं?",
            "ru-RU": "Я не понял. Не могли бы вы повторить?",
            "pt-BR": "Não entendi. Você poderia repetir, por favor?",
        }
        response.say(
            fallback_messages.get(current_lang, fallback_messages["en-US"]),
            voice=voice,
            language=current_lang
        )
        gather = Gather(
            input="speech",
            action="/process-speech",
            method="POST",
            speech_timeout="auto",
            language="auto"  # Continue auto-detecting
        )
        response.append(gather)
        return str(response), 200, {"Content-Type": "text/xml"}
    
    # Process with agent (Grok will respond in the detected language)
    agent_response = agent.process_message(call_sid, speech_result)
    
    # Create TwiML response with appropriate voice
    response = VoiceResponse()
    response.say(agent_response, voice=voice, language=current_lang)
    
    # Continue conversation with language detection
    gather = Gather(
        input="speech",
        action="/process-speech",
        method="POST",
        speech_timeout="auto",
        language="auto",  # Auto-detect language
        hints="menu, order, price, burger, salad, pasta, dessert, chicken, salmon, beef, yes, no, add, remove, review, checkout, menú, orden, menù, ordine, メニュー, 注文, 菜单, 订单, قائمة, طلب, منو, سفارش, بله, نه"
    )
    response.append(gather)
    
    # Fallback
    fallback_messages = {
        "en-US": "Is there anything else I can help you with?",
        "es-ES": "¿Hay algo más en lo que pueda ayudarle?",
        "fr-FR": "Y a-t-il autre chose avec laquelle je peux vous aider?",
        "de-DE": "Gibt es noch etwas, womit ich Ihnen helfen kann?",
        "it-IT": "C'è qualcos'altro con cui posso aiutarti?",
        "ja-JP": "他に何かお手伝いできることはありますか？",
        "zh-CN": "还有什么我可以帮助您的吗？",
        "ar-SA": "هل هناك أي شيء آخر يمكنني مساعدتك فيه؟",
        "fa-IR": "چیز دیگری هست که بتوانم کمکتان کنم؟",
        "hi-IN": "क्या मैं आपकी और किसी चीज़ में मदद कर सकता हूं?",
        "ru-RU": "Могу ли я еще чем-то помочь?",
        "pt-BR": "Há mais alguma coisa com que eu possa ajudá-lo?",
    }
    response.say(
        fallback_messages.get(current_lang, fallback_messages["en-US"]),
        voice=voice,
        language=current_lang
    )
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
        if call_sid in call_languages:
            del call_languages[call_sid]
    
    return "", 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)



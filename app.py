"""
Flask application for Four Seasons Room Service Phone Agent
Handles Twilio webhooks for incoming calls
"""

from flask import Flask, request, send_file
from twilio.twiml.voice_response import VoiceResponse, Gather, Play
from twilio.rest import Client
import os
import tempfile
import uuid
import time
import threading
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from agent import RoomServiceAgent
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
agent = RoomServiceAgent()

# Store detected language per call
call_languages = {}

# OpenAI client for TTS
openai_client = None
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key and openai_key != "your_openai_api_key":
    openai_client = OpenAI(api_key=openai_key)

# Store generated audio files temporarily with metadata for cleanup
audio_cache = {}  # {audio_id: {"path": str, "created": datetime, "text_hash": str}}

# Cache common responses to avoid regenerating
response_cache = {}  # {text_hash: audio_id}

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    version = get_version_timestamp()
    return f"Four Seasons Room Service Agent is running! Version: {version}", 200


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
        "fa-IR": "Zeina",  # Farsi/Persian - use Arabic voice (closest available)
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

def get_openai_tts_voice(lang_code):
    """Get OpenAI TTS voice for language - optimized for each language's characteristics"""
    # OpenAI TTS voices: alloy (neutral), echo (bright), fable (warm), onyx (deep), nova (smooth), shimmer (clear)
    # Optimized voice selection based on language phonetics and cultural preferences
    voice_map = {
        "en-US": "nova",  # Smooth, professional English
        "es-ES": "shimmer", "es-MX": "shimmer", "es-US": "shimmer",  # Clear, expressive
        "fr-FR": "alloy", "fr-CA": "alloy",  # Neutral, elegant
        "de-DE": "onyx",  # Deep, authoritative
        "it-IT": "echo",  # Bright, expressive
        "pt-BR": "fable", "pt-PT": "fable",  # Warm, friendly
        "ja-JP": "nova",  # Smooth, respectful
        "ko-KR": "shimmer",  # Clear, polite
        "zh-CN": "alloy", "zh-TW": "alloy",  # Neutral, clear
        "ar-SA": "onyx", "ar-EG": "onyx",  # Deep, respectful
        "fa-IR": "alloy",  # OpenAI TTS handles Farsi excellently with alloy voice
        "hi-IN": "shimmer",  # Clear, warm
        "ru-RU": "onyx",  # Deep, formal
        "nl-NL": "echo",  # Bright, friendly
        "pl-PL": "fable",  # Warm, clear
        "tr-TR": "alloy",  # Neutral, clear
        "sv-SE": "nova",  # Smooth, clear
        "da-DK": "echo",  # Bright, friendly
        "no-NO": "fable",  # Warm, clear
        "fi-FI": "shimmer",  # Clear, precise
        "cs-CZ": "onyx",  # Deep, clear
        "hu-HU": "echo",  # Bright, expressive
        "ro-RO": "fable",  # Warm, friendly
        "th-TH": "alloy",  # Neutral, clear
        "vi-VN": "shimmer"  # Clear, expressive
    }
    return voice_map.get(lang_code, "nova")  # Default to nova (most versatile)

def cleanup_old_audio():
    """Remove audio files older than 1 hour"""
    try:
        current_time = datetime.now()
        to_remove = []
        for audio_id, metadata in audio_cache.items():
            if current_time - metadata["created"] > timedelta(hours=1):
                try:
                    if os.path.exists(metadata["path"]):
                        os.remove(metadata["path"])
                    to_remove.append(audio_id)
                except Exception as e:
                    print(f"Error removing audio file {audio_id}: {e}")
        
        for audio_id in to_remove:
            del audio_cache[audio_id]
            # Also remove from response cache if present
            if metadata.get("text_hash") in response_cache:
                del response_cache[metadata["text_hash"]]
    except Exception as e:
        print(f"Error in cleanup: {e}")

def get_version_timestamp():
    """Get current timestamp in Eastern Time formatted as YY-MM-DD-HHMM"""
    try:
        et = pytz.timezone('US/Eastern')
        now_et = datetime.now(et)
        # Format: YY-MM-DD-HHMM (e.g., 25-11-20-1430)
        version = now_et.strftime("%y-%m-%d-%H%M")
        return version
    except Exception as e:
        print(f"Error getting version timestamp: {e}")
        # Fallback to UTC if ET fails
        return datetime.utcnow().strftime("%y-%m-%d-%H%M")

def get_base_url():
    """Get the base URL for the service - prefer environment variable, fallback to request"""
    # Check environment variable first (set in Render)
    base_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("BASE_URL")
    if base_url:
        return base_url.rstrip('/')
    # Fallback to request URL
    try:
        if request:
            return request.url_root.rstrip('/')
    except:
        pass
    # Last resort - use the known Render URL
    return "https://four-seasons-room-service-1.onrender.com"

def generate_audio_with_openai(text, lang_code, base_url):
    """Generate high-quality audio using OpenAI TTS with caching and cleanup"""
    if not openai_client:
        print("OpenAI client not available for TTS")
        return None
    
    try:
        # Create hash for caching
        import hashlib
        text_hash = hashlib.md5(f"{text}_{lang_code}".encode()).hexdigest()
        
        # Check cache first
        if text_hash in response_cache:
            cached_id = response_cache[text_hash]
            if cached_id in audio_cache:
                # Update access time
                audio_cache[cached_id]["created"] = datetime.now()
                print(f"Using cached audio for text hash: {text_hash[:8]}...")
                return cached_id
        
        print(f"Generating new audio for language {lang_code}, text length: {len(text)}")
        voice = get_openai_tts_voice(lang_code)
        
        # Use HD model for superior quality
        response = openai_client.audio.speech.create(
            model="tts-1-hd",  # High-definition quality
            voice=voice,
            input=text,
            speed=0.95  # Slightly slower for clarity
        )
        
        # Save to temporary file
        audio_id = str(uuid.uuid4())
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3', dir=tempfile.gettempdir())
        temp_file.write(response.content)
        temp_file.close()
        
        file_size = os.path.getsize(temp_file.name)
        print(f"Generated audio file: {audio_id}, size: {file_size} bytes, path: {temp_file.name}")
        
        # Verify file is not empty
        if file_size == 0:
            print(f"ERROR: Generated audio file is empty for {audio_id}")
            os.remove(temp_file.name)
            return None
        
        # Store in cache with metadata
        audio_cache[audio_id] = {
            "path": temp_file.name,
            "created": datetime.now(),
            "text_hash": text_hash
        }
        response_cache[text_hash] = audio_id
        
        # Cleanup old files in background (non-blocking)
        threading.Thread(target=cleanup_old_audio, daemon=True).start()
        
        return audio_id
    except Exception as e:
        print(f"Error generating OpenAI TTS audio: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route("/audio/<audio_id>")
def serve_audio(audio_id):
    """Serve generated audio file with proper headers"""
    print(f"Audio request received for ID: {audio_id}")
    if audio_id in audio_cache:
        metadata = audio_cache[audio_id]
        file_path = metadata.get("path") if isinstance(metadata, dict) else metadata
        if file_path and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"Serving audio file: {audio_id}, size: {file_size} bytes")
            if file_size == 0:
                print(f"ERROR: Audio file is empty: {audio_id}")
                return "Audio file is empty", 500
            response = send_file(file_path, mimetype='audio/mpeg')
            # Add cache headers for better performance
            response.headers['Cache-Control'] = 'public, max-age=3600'
            response.headers['Content-Type'] = 'audio/mpeg'
            response.headers['Content-Length'] = str(file_size)
            return response
        else:
            print(f"Audio file not found on disk: {file_path}")
    else:
        print(f"Audio ID not in cache: {audio_id}, cache size: {len(audio_cache)}")
    return "Audio not found", 404

def say_with_openai_tts(response, text, lang_code, base_url):
    """Use OpenAI TTS instead of Twilio's built-in TTS for superior voice quality"""
    if not text or not text.strip():
        print("Empty text provided to TTS")
        return False
        
    if openai_client:
        try:
            print(f"Attempting OpenAI TTS for language {lang_code}, text preview: {text[:50]}...")
            audio_id = generate_audio_with_openai(text, lang_code, base_url)
            if audio_id:
                # Use absolute URL for reliable playback
                audio_url = f"{base_url}/audio/{audio_id}"
                print(f"Successfully generated audio, URL: {audio_url}")
                response.play(audio_url)
                return True
            else:
                print("OpenAI TTS returned None, falling back to Twilio")
        except Exception as e:
            print(f"OpenAI TTS failed with exception, falling back to Twilio: {e}")
            import traceback
            traceback.print_exc()
    
    # Fallback to Twilio's Say if OpenAI TTS fails
    try:
        print(f"Using Twilio TTS fallback for language {lang_code}")
        voice = get_voice_for_language(lang_code)
        twilio_lang = get_twilio_language_code(lang_code)
        response.say(text, voice=voice, language=twilio_lang)
        return False
    except Exception as e:
        print(f"Twilio TTS also failed: {e}")
        # Last resort: just say it in English
        response.say(text, voice="alice", language="en-US")
        return False

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
    
    # Get version timestamp for this call
    version = get_version_timestamp()
    
    # Initial greeting in multiple languages with version info
    greetings = {
        "en-US": f"Hello, this is Nasrin from Four Seasons room service. Version {version}. I speak multiple languages—say the language name to switch. How can I help you today?",
        "es-ES": f"Saludos desde Four Seasons. Soy Nasrin, su conserje dedicada de servicio a la habitación. Esta es la versión {version}. ¿Cómo puedo elevar su experiencia con un momento gastronómico delicioso hoy?",
        "fr-FR": f"Salutations du Four Seasons. Je suis Nasrin, votre concierge dédiée au service en chambre. Ceci est la version {version}. Comment puis-je rehausser votre expérience avec un moment de dégustation délicieux aujourd'hui?",
        "de-DE": f"Grüße vom Four Seasons. Ich bin Nasrin, Ihre persönliche Concierge für den Zimmerservice. Dies ist Version {version}. Wie kann ich Ihr Erlebnis heute mit einem köstlichen kulinarischen Moment bereichern?",
        "it-IT": f"Saluti dal Four Seasons. Sono Nasrin, la vostra concierge dedicata al servizio in camera. Questa è la versione {version}. Come posso elevare la vostra esperienza con un delizioso momento gastronomico oggi?",
        "ja-JP": f"フォーシーズンズよりご挨拶申し上げます。ルームサービスの専属コンシェルジュ、ナスリンでございます。これはバージョン{version}です。本日、素晴らしい食事のひとときでお客様の体験をより豊かにするには、どのようにお手伝いできるでしょうか？",
        "zh-CN": f"来自四季酒店的问候。我是纳斯林，您专属的客房服务礼宾。这是版本{version}。今天，我如何通过美妙的用餐时刻来提升您的体验？",
        "ar-SA": f"تحيات من فور سيزونز. أنا نسرين، كونسيرج خدمة الغرف المخصصة لك. هذه هي النسخة {version}. كيف يمكنني رفع تجربتك مع لحظة طعام لذيذة اليوم؟",
        "fa-IR": f"درود از فور سیزونز. من نسرین هستم، کونسیرژ اختصاصی سرویس اتاق شما. این نسخه {version} است. امروز چگونه می‌توانم تجربه شما را با یک لحظه لذیذ غذایی ارتقا دهم؟",
        "hi-IN": f"फोर सीज़न्स से अभिवादन। मैं नसरीन हूं, आपकी समर्पित रूम सर्विस कॉन्सिएर्ज। यह संस्करण {version} है। आज मैं एक स्वादिष्ट भोजन के क्षण के साथ आपके अनुभव को कैसे बढ़ा सकती हूं?",
        "ru-RU": f"Приветствие от Four Seasons. Я Насрин, ваш персональный консьерж службы номеров. Это версия {version}. Как я могу улучшить ваше впечатление сегодня с помощью восхитительного кулинарного момента?",
        "pt-BR": f"Saudações do Four Seasons. Sou Nasrin, sua concierge dedicada de serviço de quarto. Esta é a versão {version}. Como posso elevar sua experiência com um momento gastronômico delicioso hoje?",
    }
    
    # Start with greeting using OpenAI TTS for superior voice quality
    base_url = get_base_url()
    greeting_text = greetings.get(default_lang, greetings["en-US"])
    say_with_openai_tts(response, greeting_text, default_lang, base_url)
    
    # Gather user input - support multiple languages
    # Twilio will auto-detect language, but we can specify multiple
    gather = Gather(
        input="speech",
        action="/process-speech",
        method="POST",
        speech_timeout="auto",
        language="auto",  # Auto-detect language
        hints="menu, order, price, burger, salad, pasta, dessert, chicken, salmon, beef, menú, orden, precio, menù, ordine, prezzo, メニュー, 注文, 価格, 菜单, 订单, 价格, قائمة, طلب, سعر, منو, سفارش, قیمت, فهرست, غذا, نوشیدنی, صبحانه, ناهار, شام, پیش غذا, دسر, نوشابه, آب, چای, قهوه"
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
    
    # Log what Twilio transcribed
    print(f"Twilio transcribed for call {call_sid}: '{speech_result}'")
    
    # Check for explicit language change requests FIRST, before any other processing
    language_switch_keywords = {
        "farsi": "fa-IR", "persian": "fa-IR", "فارسی": "fa-IR",
        "far see": "fa-IR", "farcy": "fa-IR", "farsy": "fa-IR",  # Common mis-transcriptions
        "english": "en-US", "انگلیسی": "en-US",
        "spanish": "es-ES", "español": "es-ES",
        "french": "fr-FR", "français": "fr-FR",
        "german": "de-DE", "deutsch": "de-DE",
        "italian": "it-IT", "italiano": "it-IT",
        "japanese": "ja-JP", "日本語": "ja-JP",
        "chinese": "zh-CN", "中文": "zh-CN",
        "arabic": "ar-SA", "عربي": "ar-SA",
        "hindi": "hi-IN", "हिन्दी": "hi-IN",
        "russian": "ru-RU", "русский": "ru-RU",
        "portuguese": "pt-BR", "português": "pt-BR",
    }
    
    speech_lower = speech_result.lower().strip() if speech_result else ""
    
    # Check if user is requesting a language change - be more lenient
    # First, check if message is very short and matches a language keyword exactly
    if len(speech_lower.split()) <= 2:  # Short message (1-2 words)
        for keyword, lang_code in language_switch_keywords.items():
            if keyword in speech_lower and (speech_lower == keyword or speech_lower.startswith(keyword) or speech_lower.endswith(keyword)):
                call_languages[call_sid] = lang_code
                print(f"User requested language switch to {lang_code} for call {call_sid}. Original message: '{speech_result}'")
                # Acknowledge language change
                response = VoiceResponse()
                lang_confirmations = {
                    "fa-IR": "بله، حالا به فارسی صحبت می‌کنم. چطور می‌توانم به شما کمک کنم؟",
                    "en-US": "Of course, I'll speak English. How may I assist you?",
                    "es-ES": "Por supuesto, hablaré en español. ¿Cómo puedo ayudarle?",
                    "fr-FR": "Bien sûr, je parlerai en français. Comment puis-je vous aider?",
                    "de-DE": "Natürlich, ich werde Deutsch sprechen. Wie kann ich Ihnen helfen?",
                    "it-IT": "Certamente, parlerò in italiano. Come posso aiutarti?",
                    "ja-JP": "もちろん、日本語で話します。どのようにお手伝いできますか？",
                    "zh-CN": "当然，我会说中文。我能为您做些什么？",
                    "ar-SA": "بالطبع، سأتحدث بالعربية. كيف يمكنني مساعدتك؟",
                    "hi-IN": "बिल्कुल, मैं हिंदी में बोलूंगी। मैं आपकी कैसे मदद कर सकती हूं?",
                    "ru-RU": "Конечно, я буду говорить по-русски. Чем могу помочь?",
                    "pt-BR": "Claro, falarei em português. Como posso ajudá-lo?",
                }
                current_lang = lang_code
                base_url = get_base_url()
                confirmation_text = lang_confirmations.get(lang_code, lang_confirmations["en-US"])
                say_with_openai_tts(response, confirmation_text, current_lang, base_url)
                gather = Gather(
                    input="speech",
                    action="/process-speech",
                    method="POST",
                    speech_timeout="auto",
                    language=current_lang  # Use specific language after switch
                )
                response.append(gather)
                return str(response), 200, {"Content-Type": "text/xml"}
    
    # Check if message contains language switch phrases
    for keyword, lang_code in language_switch_keywords.items():
        # Check if the message is just the keyword, or contains language switch phrases
        is_language_request = (
            speech_lower == keyword or
            speech_lower == f"speak {keyword}" or
            speech_lower == f"use {keyword}" or
            speech_lower == f"switch to {keyword}" or
            speech_lower == f"switch {keyword}" or
            f"speak {keyword}" in speech_lower or
            f"use {keyword}" in speech_lower or
            f"switch to {keyword}" in speech_lower
        )
        
        if is_language_request:
            call_languages[call_sid] = lang_code
            print(f"User requested language switch to {lang_code} for call {call_sid}. Original message: '{speech_result}'")
            # Acknowledge language change
            response = VoiceResponse()
            lang_confirmations = {
                "fa-IR": "بله، حالا به فارسی صحبت می‌کنم. چطور می‌توانم به شما کمک کنم؟",
                "en-US": "Of course, I'll speak English. How may I assist you?",
                "es-ES": "Por supuesto, hablaré en español. ¿Cómo puedo ayudarle?",
                "fr-FR": "Bien sûr, je parlerai en français. Comment puis-je vous aider?",
                "de-DE": "Natürlich, ich werde Deutsch sprechen. Wie kann ich Ihnen helfen?",
                "it-IT": "Certamente, parlerò in italiano. Come posso aiutarti?",
                "ja-JP": "もちろん、日本語で話します。どのようにお手伝いできますか？",
                "zh-CN": "当然，我会说中文。我能为您做些什么？",
                "ar-SA": "بالطبع، سأتحدث بالعربية. كيف يمكنني مساعدتك؟",
                "hi-IN": "बिल्कुल, मैं हिंदी में बोलूंगी। मैं आपकी कैसे मदद कर सकती हूं?",
                "ru-RU": "Конечно, я буду говорить по-русски. Чем могу помочь?",
                "pt-BR": "Claro, falarei em português. Como posso ajudá-lo?",
            }
            current_lang = lang_code
            base_url = get_base_url()
            confirmation_text = lang_confirmations.get(lang_code, lang_confirmations["en-US"])
            say_with_openai_tts(response, confirmation_text, current_lang, base_url)
            gather = Gather(
                input="speech",
                action="/process-speech",
                method="POST",
                speech_timeout="auto",
                language=current_lang  # Use specific language after switch
            )
            response.append(gather)
            return str(response), 200, {"Content-Type": "text/xml"}
    
    # Detect language from Twilio (if available) or use stored/default
    detected_lang = request.form.get("SpeechLanguage", None)
    if detected_lang:
        # Only update if we haven't explicitly set a language
        if call_sid not in call_languages or call_languages[call_sid] == "en-US":
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
    
    # Create TwiML response with OpenAI TTS for superior voice quality
    response = VoiceResponse()
    base_url = get_base_url()
    say_with_openai_tts(response, agent_response, current_lang, base_url)
    
    # Continue conversation with language detection
    gather = Gather(
        input="speech",
        action="/process-speech",
        method="POST",
        speech_timeout="auto",
        language="auto",  # Auto-detect language
        hints="menu, order, price, burger, salad, pasta, dessert, chicken, salmon, beef, yes, no, add, remove, review, checkout, menú, orden, menù, ordine, メニュー, 注文, 菜单, 订单, قائمة, طلب, منو, سفارش, بله, نه, فهرست, غذا, قیمت, اضافه, حذف, بررسی, پرداخت"
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



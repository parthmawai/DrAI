import os
from flask import Flask, request, session, jsonify
import google.generativeai as genai
from twilio.twiml.voice_response import VoiceResponse, Gather, Play, Say
from dotenv import load_dotenv
import re
from datetime import datetime
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key") # For session management

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Medical Context Prompts
MEDICAL_PROMPT_EN = """
You are a highly professional, empathetic, and efficient AI health assistant. Your primary goal is to help the patient quickly and smoothly book an appointment with the appropriate healthcare specialist based on their symptoms.

Current Date and Time: {current_datetime}
User Location: Noida, Uttar Pradesh, India

Guidelines:
- Never provide definitive diagnoses.
- Always recommend consulting a healthcare professional for accurate diagnosis and treatment.
- If the user's initial description of symptoms is vague or unclear, ask ONLY ONE relevant clarifying question at a time to gather essential information before suggesting a specialist. Be crisp, polite, and professional in your responses.
- Once you have a reasonable understanding of the patient's condition (typically after the initial description and perhaps one clarifying question), promptly suggest the most relevant medical specialty.
- Immediately after suggesting a specialist, ask the user if they would like to book an appointment.
- Consider the entire conversation history to maintain context.

User Symptoms: {symptoms}

Conversation History:
{history}

Provide a response covering:
- If the initial symptoms are unclear, ask ONLY ONE relevant clarifying question.
- Otherwise, provide:
    1. Potential health concerns (very briefly).
    2. The most relevant medical specialty the user should consult.
    3. A clear and concise question asking if the user would like to book an appointment with the suggested specialist.
"""

MEDICAL_PROMPT_HI = """
आप एक अत्यधिक पेशेवर, सहानुभूतिपूर्ण और कुशल एआई स्वास्थ्य सहायक हैं। आपका प्राथमिक लक्ष्य रोगी को उनके लक्षणों के आधार पर उचित स्वास्थ्य सेवा विशेषज्ञ के साथ जल्दी और आसानी से अपॉइंटमेंट बुक करने में मदद करना है।

वर्तमान तिथि और समय: {current_datetime}
उपयोगकर्ता का स्थान: नोएडा, उत्तर प्रदेश, भारत

दिशानिर्देश:
- कभी भी निश्चित निदान प्रदान न करें।
- हमेशा सटीक निदान और उपचार के लिए एक स्वास्थ्य देखभाल पेशेवर से परामर्श करने की सलाह दें।
- यदि उपयोगकर्ता का लक्षणों का प्रारंभिक विवरण अस्पष्ट या अपर्याप्त है, तो विशेषज्ञ का सुझाव देने से पहले आवश्यक जानकारी एकत्र करने के लिए एक समय में केवल एक प्रासंगिक स्पष्ट करने वाला प्रश्न पूछें। अपनी प्रतिक्रियाओं में संक्षिप्त, विनम्र और पेशेवर रहें।
- एक बार जब आपको रोगी की स्थिति की उचित समझ हो जाती है (आमतौर पर प्रारंभिक विवरण और शायद एक स्पष्ट करने वाले प्रश्न के बाद), तो तुरंत सबसे प्रासंगिक चिकित्सा विशेषता का सुझाव दें।
- विशेषज्ञ का सुझाव देने के तुरंत बाद, उपयोगकर्ता से पूछें कि क्या वे अपॉइंटमेंट बुक करना चाहेंगे।
- संदर्भ बनाए रखने के लिए पूरी बातचीत के इतिहास पर विचार करें।

उपयोगकर्ता के लक्षण: {symptoms}

बातचीत का इतिहास:
{history}

एक प्रतिक्रिया प्रदान करें जिसमें शामिल हों:
- यदि प्रारंभिक लक्षण अस्पष्ट हैं, तो केवल एक प्रासंगिक स्पष्ट करने वाला प्रश्न पूछें।
- अन्यथा, प्रदान करें:
    1. संभावित स्वास्थ्य चिंताएं (बहुत संक्षेप में)।
    2. सबसे प्रासंगिक चिकित्सा विशेषता जिससे उपयोगकर्ता को परामर्श करना चाहिए।
    3. एक स्पष्ट और संक्षिप्त प्रश्न जो पूछता है कि क्या उपयोगकर्ता सुझाए गए विशेषज्ञ के साथ अपॉइंटमेंट बुक करना चाहेंगे।
"""

@app.route("/voice", methods=["POST"])
def voice():
    """Handle incoming voice calls and ask for language preference"""
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/set_language",
        timeout=5,
        num_digits=1 # To handle potential DTMF input if speech recognition fails
    )
    gather.say("Hello! Welcome to our AI Health Companion. Please say 'English' for English and 'Hindi' for Hindi", language="en")
    response.append(gather)
    return str(response)

@app.route("/set_language", methods=["POST"])
def set_language():
    """Sets the language for the session based on user input"""
    speech_result = request.form.get("SpeechResult", "").strip().lower()
    digits = request.form.get("Digits")

    language = None
    if "hindi" in speech_result or digits == "2": # Assuming '2' could be a fallback for Hindi
        language = "hi-IN"
        initial_message = "नमस्ते! मैं आपका एआई स्वास्थ्य सहायक हूँ। कृपया अपने लक्षणों का वर्णन करें।"
    elif "english" in speech_result or digits == "1": # Assuming '1' could be a fallback for English
        language = "en-IN"
        initial_message = "Namaste! I'm your AI Health Companion. Please describe your symptoms."
    else:
        response = VoiceResponse()
        response.say("Sorry, I didn't understand your language preference. Please try again.", language="en")
        response.redirect("/voice")
        return str(response)

    session['language'] = language
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/process",
        timeout=5,
        language=language
    )
    gather.say(initial_message, language=language.split('-')[0]) # Set voice language based on selection
    response.append(gather)
    return str(response)

@app.route("/process", methods=["POST"])
def process():
    print("Received POST request to /process")
    print("Form data:", request.form)
    user_speech = request.form.get("SpeechResult", "").strip().lower()
    language = session.get('language', 'en-IN')

    if 'conversation_history' not in session:
        session['conversation_history'] = []
        session['initial_symptoms'] = user_speech # Store initial symptoms

    session['conversation_history'].append({"role": "user", "content": user_speech})

    user_speech = user_speech.strip()

    if not user_speech:
        return _error_response("Sorry, I couldn't understand you.")

    if ("book" in user_speech and "appointment" in user_speech) or ("schedule" in user_speech and "appointment" in user_speech):
        return _book_appointment_flow(specialist=session.get('suggested_specialist')) # Pass the specialist

    try:
        return _get_gemini_response(user_speech)

    except Exception as e:
        print(f"Error processing request: {e}")
        return _error_response("Technical difficulties. Please try again.")

def _get_gemini_response(user_speech):
    language = session.get('language', 'en-IN')
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')

        history_text = "\n".join([f"{item['role']}: {item['content']}" for item in session['conversation_history']])
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if language == "hi-IN":
            prompt = MEDICAL_PROMPT_HI.format(symptoms=user_speech, history=history_text, current_datetime=current_datetime)
        else:
            prompt = MEDICAL_PROMPT_EN.format(symptoms=user_speech, history=history_text, current_datetime=current_datetime)

        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 300
        }

        gemini_response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        ai_reply = gemini_response.text
        session['conversation_history'].append({"role": "assistant", "content": ai_reply})

        print(f"\n--- Gemini Response ({language}) ---")
        print(ai_reply)
        print("--- End of Gemini Response ---\n")

        # Extract specialist for booking
        specialist = ""
        if language == "en-IN":
            specialist_match = re.search(r"consult a (.*?) specialist", ai_reply, re.IGNORECASE)
            if specialist_match:
                specialist = specialist_match.group(1).strip()
        elif language == "hi-IN":
            specialist_match = re.search(r"परामर्श करना चाहिए (.*?) विशेषज्ञ", ai_reply, re.IGNORECASE)
            if specialist_match:
                specialist = specialist_match.group(1).strip()
        session['suggested_specialist'] = specialist

        # Check if the user wants to book an appointment based on Gemini's suggestion
        if "yes" in user_speech.lower() and ("book" in ai_reply.lower() or "schedule" in ai_reply.lower()):
            return _book_appointment_flow(specialist=specialist) # Pass the extracted specialist

        return _speak_response(ai_reply)

    except Exception as e:
        print(f"Error processing request: {e}")
        return _error_response("Technical difficulties. Please try again.")

def _speak_response(text):
    """Generate voice response and check for appointment booking request"""
    print(f"Raw Gemini output: '{text}'") # Log raw output

    # Clean the chatbot speech (Gemini's response)
    cleaned_text = re.sub(r"^(/[a-zA-Z0-9]+)", "", text).strip() # Remove leading /alphanumeric
    cleaned_text = re.sub(r"(/[a-zA-Z0-9]+)$", "", cleaned_text).strip() # Remove trailing /alphanumeric

    print(f"Cleaned Gemini output: '{cleaned_text}'") # Log cleaned output

    response = VoiceResponse()
    language = session.get('language', 'en-IN')
    voice = "Polly.Aditi" if language == "en-IN" else "Polly.Aditi"

    response.say(f'{cleaned_text}', voice=voice, language=language.split('-')[0])
    response.play("https://www.soundjay.com/buttons/sounds/beep-07a.mp3") # Placeholder beep sound

    gather = Gather(
        input="speech",
        action="/process",
        timeout=5,
        language=language
    )
    response.append(gather)

    return str(response)

def _book_appointment_flow(specialist="healthcare specialist"): # Set a default value
    """Handles the appointment booking flow"""
    session['BOOKING_INFO'] = {} # Initialize booking info for a new booking
    response = VoiceResponse()
    language = session.get('language', 'en-IN')
    specialist_prompt = f" with a {specialist}" if specialist else ""
    specialist_prompt_hi = f" {specialist} के साथ" if specialist else ""

    if language == "hi-IN":
        response.say(f"ज़रूर, चलिए आपकी{specialist_prompt_hi} अपॉइंटमेंट बुक करते हैं।", language="hi")
        gather = Gather(
            input="speech",
            action="/collect_booking_info",
            timeout=5,
            language=language
        )
        gather.say("सबसे पहले, कृपया अपना पूरा नाम बताएं।", language="hi")
        response.append(gather)
    else:
        response.say(f"Okay, let's book your appointment{specialist_prompt}.", language="en")
        gather = Gather(
            input="speech",
            action="/collect_booking_info",
            timeout=5,
            language=language
        )
        gather.say("First, please tell me your full name.")
        response.append(gather)
    return str(response)

def _confirm_booking():
    """Confirms the booking with the user"""
    language = session.get('language', 'en-IN')
    BOOKING_INFO = session.get('BOOKING_INFO', {})
    name = BOOKING_INFO.get("name", "there")
    age = BOOKING_INFO.get("age", "not specified")
    location = BOOKING_INFO.get("location", "not specified")
    date = BOOKING_INFO.get("date", "not specified")
    time = BOOKING_INFO.get("time", "not specified")
    specialist = session.get('suggested_specialist', 'healthcare specialist') # Get specialist from session
    conversation_history = session.get('conversation_history', [])
    latest_symptoms = ""
    for item in reversed(conversation_history):
        if item['role'] == 'user':
            latest_symptoms = item['content']
            break
    if not latest_symptoms:
        latest_symptoms = session.get('initial_symptoms', 'Not specified') # Fallback to initial symptoms

    specialist_text = f" with a {specialist}" if specialist else ""
    specialist_text_hi = f" {specialist} के साथ" if specialist else ""

    booking_result = Book_Appointment(name, age, location, date, time, latest_symptoms, specialist)

    response = VoiceResponse()
    if language == "hi-IN":
        response.say(f"ठीक है {name}, हमें आपकी जानकारी मिल गई है। आपकी आयु {age} वर्ष है और पसंदीदा स्थान {location} है। आपने {date} को {time} बजे{specialist_text_hi} अपॉइंटमेंट बुक किया है। {booking_result}", language="hi")
        response.say("हमारी सेवा का उपयोग करने के लिए धन्यवाद।", language="hi")
    else:
        response.say(f"Okay {name}, we have received your details. Your age is {age} and preferred location is {location}. You have booked an appointment for {date} at {time}{specialist_text}. {booking_result}")
        response.say("Thank you for using our service.")

    response.hangup()
    return str(response)

def Book_Appointment(name, age, location, date, time, symptoms, specialist):
    """Book appointment and save to database via API"""
    appointment_data = {
        "name": name,
        "age": age,
        "location": location,
        "date": date,
        "time": time,
        "specialist": specialist,
        "symptoms": symptoms
    }

    # Log details locally
    print("\n--- Book_Appointment Function Called ---")
    for key, value in appointment_data.items():
        print(f"{key}: {value}")
    print("--- End of Details ---\n")

    # Try to save to database via API
    try:
        # Replace with the actual URL of your MERN backend API
        api_url = "http://localhost:5000/api/appointments"
        headers = {"Content-Type": "application/json"}
        response = requests.post(api_url, json=appointment_data, headers=headers)
        if response.status_code == 200:
            return "Your appointment has been booked successfully."
        else:
            print(f"API Error: Status Code {response.status_code}, Response: {response.text}")
            return "Appointment details recorded. Our team will contact you soon."
    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: {e}")
        return "Appointment details recorded. Our team will contact you soon."

@app.route("/collect_booking_info", methods=["POST"])
def collect_booking_info():
    """Collects booking information from the user"""
    user_response = request.form.get("SpeechResult", "").strip()
    language = session.get('language', 'en-IN')
    if 'BOOKING_INFO' not in session:
        session['BOOKING_INFO'] = {}
    BOOKING_INFO = session['BOOKING_INFO']

    if not user_response:
        return _error_response("Sorry, I didn't catch that. Let's try again.")

    if "name" not in BOOKING_INFO:
        BOOKING_INFO["name"] = user_response
        session['BOOKING_INFO'] = BOOKING_INFO
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action="/collect_booking_info",
            timeout=5,
            language=language
        )
        if language == "hi-IN":
            gather.say(f"धन्यवाद, {user_response}। अब कृपया अपनी आयु बताएं।", language="hi")
        else:
            gather.say(f"Thank you, {user_response}. Now, please tell me your age.")
        response.append(gather)
        return str(response)
    elif "age" not in BOOKING_INFO:
        BOOKING_INFO["age"] = user_response
        session['BOOKING_INFO'] = BOOKING_INFO
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action="/collect_booking_info",
            timeout=5,
            language=language
        )
        if language == "hi-IN":
            gather.say("आपका सामान्य स्थान या आप किस क्षेत्र में अपॉइंटमेंट लेना चाहेंगे?", language="hi")
        else:
            gather.say("What is your general location or the area where you'd like to have your appointment?")
        response.append(gather)
        return str(response)
    elif "location" not in BOOKING_INFO:
        BOOKING_INFO["location"] = user_response
        session['BOOKING_INFO'] = BOOKING_INFO
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action="/collect_booking_info",
            timeout=5,
            language=language
        )
        if language == "hi-IN":
            gather.say("आप किस तारीख को अपॉइंटमेंट बुक करना चाहेंगे?", language="hi")
        else:
            gather.say("What date would you like to book your appointment?")
        response.append(gather)
        return str(response)
    elif "date" not in BOOKING_INFO:
        BOOKING_INFO["date"] = user_response
        session['BOOKING_INFO'] = BOOKING_INFO
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action="/collect_booking_info",
            timeout=5,
            language=language
        )
        if language == "hi-IN":
            gather.say("और उस तारीख को किस समय आप अपॉइंटमेंट लेना चाहेंगे?", language="hi")
        else:
            gather.say("And what time on that date would you prefer for your appointment?")
        response.append(gather)
        return str(response)
    elif "time" not in BOOKING_INFO:
        BOOKING_INFO["time"] = user_response
        session['BOOKING_INFO'] = BOOKING_INFO
        return _confirm_booking()
    else:
        return _error_response("Something went wrong with collecting your information.")

def _error_response(message):
    """Handle errors"""
    response = VoiceResponse()
    language = session.get('language', 'en-IN')
    response.say(message, language=language.split('-')[0])
    response.redirect("/voice")
    return str(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
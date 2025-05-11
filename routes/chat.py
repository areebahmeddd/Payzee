from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from google.generativeai import GenerativeModel
import google.generativeai as genai
from pathlib import Path
import os
import json
from gtts import gTTS
from langdetect import detect
import pandas as pd

router = APIRouter()

# Configure Google AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')
chat = model.start_chat(history=[])

# Language mapping for TTS
LANGUAGE_MAP = {
    "en": {"name": "English", "gtts": "en-in"},
    "hi": {"name": "Hindi", "gtts": "hi"},
    "te": {"name": "Telugu", "gtts": "te"},
    "kn": {"name": "Kannada", "gtts": "kn"},
    "bn": {"name": "Bengali", "gtts": "bn"},
    "gu": {"name": "Gujarati", "gtts": "gu"},
    "ml": {"name": "Malayalam", "gtts": "ml"},
    "mr": {"name": "Marathi", "gtts": "mr"},
    "ta": {"name": "Tamil", "gtts": "ta"},
    "ur": {"name": "Urdu", "gtts": "ur"}
}

def detect_language(text):
    try:
        lang = detect(text)
        return lang if lang in LANGUAGE_MAP else "en"
    except:
        return "en"

def text_to_speech(text, language=None, output_file="output2.mp3"):
    lang_code = LANGUAGE_MAP[language]["gtts"] if language in LANGUAGE_MAP else LANGUAGE_MAP[detect_language(text)]["gtts"]
    lang_name = LANGUAGE_MAP.get(language, LANGUAGE_MAP[detect_language(text)])["name"]
    print(f"Converting text to speech in {lang_name}...")
    
    tts = gTTS(text=text, lang=lang_code)
    tts.save(output_file)
    print('saved')

def stt(file):
    myfile = genai.upload_file(path=file)
    prompt = 'Generate a transcript of the speech.'
    response = model.generate_content([prompt, myfile])
    return response.text

def llmcall(question, user_profile):
    """Create and return a chat instance with context."""
    context = ""
    
    # Load context from file
    with open(Path("routes/chat_data/context.txt"), 'r', encoding='utf-8') as f:
        context += f.read()
    
    # Load market price data
    df = pd.read_csv(Path("routes/chat_data/market_price.csv"))
    data_list = df.to_dict('records')
    market = str(data_list)
    
    system_prompt = f"""You are a helpful assistant that provides information about various government schemes, market prices and digital literacy from different states in India. 
    Use the following context and your knowledge to answer questions about these schemes. Provide a very clean output without any special characters. Also give relevant information according to the user profile. Refer to marker prices of different commodities in different regions in this file {market}
    User Profile:
    {user_profile}
    Context:
    {context}
    """
    
    chat.send_message(system_prompt)
    response = chat.send_message(question)
    return response.text

@router.post("/")
async def chat_endpoint(file: UploadFile = File(...), user_profile_json: str = Form(...)):
    try:
        user_profile = json.loads(user_profile_json)
    except json.JSONDecodeError as e:
        return {"error": "Invalid user profile JSON", "details": str(e)}
    
    file_path = f"temp_{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    text = stt(file_path)
    reply = llmcall(text, user_profile)
    
    tts = text_to_speech(reply, language=detect_language(reply), output_file="response.mp3")
    
    return FileResponse("response.mp3", media_type="audio/mpeg", filename="response.mp3")

"""
Payzee Chatbot Module - Provides AI-based chat functionality with speech-to-text
and text-to-speech capabilities for government scheme information.
"""
from google.generativeai import GenerativeModel, configure
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
from gtts import gTTS
from langdetect import detect
import os
import json
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')
chat = model.start_chat(history=[])

# Initialize module path
MODULE_DIR = Path(__file__).parent
def stt(file):

    myfile = genai.upload_file(path=file)
    prompt = 'Generate a transcript of the speech.'
    response = model.generate_content([prompt, myfile])
    return response.text

def llmcall(question,user_profile):
    """Create and return a chat instance with context."""
    context = ""
    # base_path = Path("state")

    # states = ["andhra-pradesh", "karnataka", "kerala", "tamilnadu", "telangana", "central"]

    # for state in states:
    #     combined_file = base_path / f"{state}_combined.txt"
    #     if combined_file.exists():
    #         with open(combined_file, 'r', encoding='utf-8') as f:
    #             context += f"\n\n=== {state.upper()} SCHEMES ===\n"
    #             context += f.read()
    # print(context)
    # output_file = Path("state") / "all_states_combined.txt"
    # with open(output_file, 'w', encoding='utf-8') as out_f:
    #     out_f.write(context)
    with open("context.txt",'r',encoding='utf-8') as f:
        context+=f.read()

    df=pd.read_csv("market_price.csv")
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

    # return tts


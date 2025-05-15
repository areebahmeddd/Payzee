import os
import json
import pandas as pd
from google import genai
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from langdetect import detect
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Configure Gemini API
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
router = APIRouter()

# Language code mapping for text-to-speech conversion
LANGUAGE_MAP = {
    "en": {"gtts": "en-in"},  # English
    "hi": {"gtts": "hi"},  # Hindi
    "kn": {"gtts": "kn"},  # Kannada
    "ml": {"gtts": "ml"},  # Malayalam
    "ta": {"gtts": "ta"},  # Tamil
    "te": {"gtts": "te"},  # Telugu
    "gu": {"gtts": "gu"},  # Gujarati
    "mr": {"gtts": "mr"},  # Marathi
    "bn": {"gtts": "bn"},  # Bengali
}


@router.post("/")
async def chat(
    file: UploadFile = File(...), user_profile: str = Form(...)
) -> FileResponse:
    try:
        # Parse and validate user profile JSON
        user_profile = json.loads(user_profile)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid user profile JSON: {str(e)}"
        )

    # Save uploaded audio file to a temporary path
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        # Pipeline: Audio → Text → Response → Speech
        query_text = convert_audio_to_text(file_path)
        response_text = generate_response(query_text, user_profile)
        detected_language = get_language_code(response_text)
        response_file = generate_speech(response_text, language=detected_language)  # noqa: F841

        # Return audio response as file
        return FileResponse(
            "response.mp3", media_type="audio/mpeg", filename="response.mp3"
        )
    finally:
        # Clean up temporary audio file
        if os.path.exists(file_path):
            os.remove(file_path)


def convert_audio_to_text(file_path: str) -> str:
    try:
        # Upload audio file and request transcription
        audio_file = client.files.upload(path=file_path)
        prompt = "Transcribe the following audio into clear and readable text."
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=[prompt, audio_file]
        )
        return response.text
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Speech to text conversion error: {str(e)}"
        )


def generate_response(user_query: str, user_profile: dict) -> str:
    try:
        chat = client.chats.create(model="gemini-2.0-flash")

        # Load government schemes and market data
        scheme_data = ""
        schme_file = Path("data/govt_schemes.txt")
        if schme_file.exists():
            scheme_data = schme_file.read_text(encoding="utf-8")

        market_data = "[]"
        market_file = Path("data/agri_prices.csv")
        if market_file.exists():
            df = pd.read_csv(market_file)
            market_data = str(df.to_dict("records"))

        # Build system prompt
        system_prompt = (
            "You are a helpful assistant that answers questions related to government schemes, "
            "market prices, and digital literacy across different Indian states. Use the information "
            "provided in the context and the user's profile. Refer to this market data as needed:\n"
            f"{market_data}\n\n"
            f"User Profile:\n{user_profile}\n\n"
            f"Context:\n{scheme_data}"
        )

        chat.send_message(system_prompt)
        response = chat.send_message(user_query)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {str(e)}")


def get_language_code(text):
    try:
        # Detect language of response and map to GTTS code
        detected_lang_code = detect(text)
        return LANGUAGE_MAP.get(detected_lang_code, {"gtts": "en-in"})["gtts"]
    except Exception:
        # Default to English if detection fails
        return "en-in"


def generate_speech(
    text: str, language: str = "en-in", output_file: str = "response.mp3"
) -> str:
    # Convert text response to speech using gTTS
    speech = gTTS(
        text=text, lang=language if language in LANGUAGE_MAP.values() else "en-in"
    )
    speech.save(output_file)
    return output_file

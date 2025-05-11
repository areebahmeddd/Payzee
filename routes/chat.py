from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
import json
import os
from typing import Dict, Any
import sys
from pathlib import Path

# Ensure chatbot module is in sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Import chatbot functionality
from main import stt, llmcall, text_to_speech, detect_language

# Create router
router = APIRouter()

@router.get("/")
def read_root():
    """Welcome endpoint for chatbot API."""
    return {"message": "Welcome to the Payzee Chatbot API!"}

@router.post("/")
async def chat(
    file: UploadFile = File(...),
    user_profile_json: str = Form(...)
):
    """
    Process an audio file to generate a response using the AI chatbot.

    Args:
        file: Audio file containing the user's speech
        user_profile_json: JSON string containing user profile information

    Returns:
        An audio file with the chatbot's response
    """
    try:
        # Parse user profile
        user_profile = json.loads(user_profile_json)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid user profile JSON: {str(e)}")

    # Save temporary file
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Process the audio
    try:
        # Convert speech to text
        text = stt(file_path)

        # Generate response from LLM
        reply = llmcall(text, user_profile)

        # Convert response to speech
        response_file = "response.mp3"
        text_to_speech(reply, language=detect_language(reply), output_file=response_file)

        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

        # Return audio response
        return FileResponse(response_file, media_type="audio/mpeg", filename=response_file)

    except Exception as e:
        # Clean up temporary file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

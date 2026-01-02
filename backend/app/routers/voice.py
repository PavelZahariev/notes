"""
Voice API Router
Handles voice recording and transcription endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from app.models.schemas import TranscriptionResponse
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/api/voice", tags=["voice"])
voice_service = VoiceService()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file to text
    """
    try:
        return await voice_service.transcribe_audio(file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/process")
async def process_voice_command(file: UploadFile = File(...)):
    """
    Process voice command and return response
    """
    # TODO: Implement LLM processing
    return {"message": "Voice processing endpoint", "filename": file.filename}


"""
Voice Service
Handles audio transcription using OpenAI Whisper
"""
import os
from openai import AsyncOpenAI
from fastapi import UploadFile
from app.models.schemas import TranscriptionResponse
from dotenv import load_dotenv

class VoiceService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def transcribe_audio(self, file: UploadFile) -> TranscriptionResponse:
        """
        Transcribe audio file using OpenAI Whisper (async)
        """
        try:
            # Pass the file directly to OpenAI
            # file.file is the underlying file-like object
            audio_content = await file.read()
            
            # Use async OpenAI client
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=(file.filename, audio_content, file.content_type),
                language="en"
            )
            
            # Return model-neutral structure
            return TranscriptionResponse(
                text=response.text,
                language=getattr(response, "language", "unknown")
            )
        except Exception as e:
            # Re-raise to be handled by the router
            raise e

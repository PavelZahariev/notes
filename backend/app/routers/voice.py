"""
Voice API Router
Handles voice recording and transcription endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.models.schemas import TranscriptionResponse, AgentResponse
from app.services.voice_service import VoiceService
from app.services.agent_service import AgentService
from app.services.database_service import DatabaseService
from app.core.auth import get_current_user
import traceback

router = APIRouter(prefix="/api/voice", tags=["voice"])
voice_service = VoiceService()
agent_service = AgentService()
db_service = DatabaseService()

@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Transcribe audio file to text
    """
    try:
        return await voice_service.transcribe_audio(file)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/process", response_model=AgentResponse)
async def process_voice_command(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Process voice command: transcribe audio and classify intent
    
    Flow:
    1. Transcribe audio to text
    2. Pass transcribed text to Agent Classify Intent Service
    3. Return AgentResponse with structured classification
    """
    try:
        # Step 1: Transcribe audio
        transcription = await voice_service.transcribe_audio(file)
        
        # Step 2: Classify intent using Agent Service
        agent_response = await agent_service.classify_input(
            text=transcription.text,
            context_vars=None
        )
        
        # Step 3: Automatically save if it's a NOTE
        if agent_response.intent == 'NOTE':
            # Generate embedding for the cleaned content
            embedding = await agent_service.get_embedding(agent_response.content)
            
            await db_service.create_entry(
                user_id=user.id,
                content=agent_response.content,
                intent='NOTE',
                category=agent_response.category,
                embedding=embedding
            )
        
        # Step 4: Return AgentResponse
        return agent_response
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")


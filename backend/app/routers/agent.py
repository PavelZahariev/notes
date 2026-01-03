"""
Agent Router
Endpoints for AI-powered intent classification and structured data extraction
"""
from fastapi import APIRouter, HTTPException
from ..models.schemas import AgentResponse, AgentClassifyRequest
from ..services.agent_service import AgentService

router = APIRouter(prefix="/api/agent", tags=["agent"])
agent_service = AgentService()

@router.post("/classify", response_model=AgentResponse)
async def classify_input(request: AgentClassifyRequest):
    """
    Classify user input and extract structured data
    
    This endpoint takes transcribed text and uses GPT-4o to:
    - Determine intent (NOTE, REMINDER, or QUERY)
    - Clean up the content
    - Auto-categorize the topic
    - Extract due dates (resolving relative dates like 'tomorrow')
    - Check if the instruction is complete
    - Generate clarification questions if needed
    
    Args:
        request: AgentClassifyRequest with text and optional context_vars
    
    Returns:
        AgentResponse with structured classification
    
    Example:
        {
            "text": "remind me to submit the report tomorrow",
            "context_vars": {"next_release": "2026-02-15"}
        }
    """
    try:
        result = agent_service.classify_input(
            text=request.text,
            context_vars=request.context_vars
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@router.post("/classify-with-context", response_model=AgentResponse)
async def classify_with_conversation_context(
    text: str,
    conversation_history: list[dict] = [],
    context_vars: dict = {}
):
    """
    Classify input with conversation history for context-aware processing
    
    This endpoint is useful when you need to maintain conversation context,
    such as follow-up clarifications or multi-turn dialogues.
    
    Args:
        text: The current user input
        conversation_history: Previous messages [{"role": "user"|"assistant", "content": "..."}]
        context_vars: Optional global context variables
    
    Returns:
        AgentResponse with structured classification
    """
    try:
        result = agent_service.classify_with_history(
            text=text,
            conversation_history=conversation_history,
            context_vars=context_vars
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

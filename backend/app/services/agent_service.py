"""
Agent Service - Intelligence Layer
Handles intent classification and structured data extraction using OpenAI GPT-4o
"""
import openai
from datetime import datetime
from typing import Optional
import traceback
from ..core.config import settings
from ..models.schemas import AgentResponse

class AgentService:
    """Service for AI-powered intent classification and data extraction"""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI agent"""
        return """You are a helpful assistant that classifies user voice input and extracts structured data.

Your tasks:
1. Determine the INTENT:
   - 'NOTE': A statement of fact, observation, or information to remember
   - 'REMINDER': A task or action item that needs to be done
   - 'QUERY': A question or request for information

2. Clean up the CONTENT: Remove filler words, fix grammar, and make it concise

3. Categorize the content: Assign a category like 'Work', 'Personal', 'Health', 'Finance', 'Data Persistence', etc.

4. Extract DUE_DATE for reminders:
   - If the user mentions a relative time ('tomorrow', 'next Friday', 'in 3 days'), convert it to an ISO datetime string
   - Use the current datetime provided in the user message as reference
   - If no timeframe is mentioned for a REMINDER, set due_date to null

5. Check if the instruction IS_COMPLETE:
   - For REMINDERS: If missing critical details (e.g., "when?", "who?", "what specifically?"), set is_complete to False
   - For NOTES: Usually complete unless obviously fragmented
   - For QUERIES: Check if the question is clear

6. Generate a CLARIFICATION_QUESTION if is_complete is False

Important date resolution examples:
- "tomorrow" → Add 1 day to current date
- "next Friday" → Find the next occurrence of Friday
- "in 3 days" → Add 3 days to current date
- "end of month" → Last day of current month
- "next week" → 7 days from now

Always be helpful and precise."""
    
    async def classify_input(
        self,
        text: str,
        context_vars: Optional[dict] = None
    ) -> AgentResponse:
        """
        Classify user input and extract structured data using OpenAI structured outputs
        
        Args:
            text: The transcribed text from the user
            context_vars: Optional dictionary of global context (e.g., {"next_release": "2026-02-15"})
        
        Returns:
            AgentResponse with structured classification and extraction
        """
        if context_vars is None:
            context_vars = {}
        
        # Build user message with current datetime and context
        current_time = datetime.now()
        user_message = f"""Current datetime: {current_time.isoformat()}

User input: "{text}"
"""
        
        # Add context variables if provided
        if context_vars:
            context_str = "\n".join([f"- {key}: {value}" for key, value in context_vars.items()])
            user_message += f"\nGlobal context:\n{context_str}\n"
        
        try:
            # Use OpenAI's structured output with response_format parameter (async)
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                response_format=AgentResponse,
            )
            
            # Extract the parsed response
            agent_response = completion.choices[0].message.parsed
            
            return agent_response
            
        except Exception as e:
            # Fallback response in case of error
            traceback.print_exc()
            return AgentResponse(
                intent='NOTE',
                content=text,
                category='Uncategorized',
                due_date=None,
                is_complete=False,
                clarification_question="I encountered an error processing your request. Could you please rephrase?"
            )
    
    async def classify_with_history(
        self,
        text: str,
        conversation_history: list[dict],
        context_vars: Optional[dict] = None
    ) -> AgentResponse:
        """
        Classify input with conversation history for context-aware processing
        
        Args:
            text: The current user input
            conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}]
            context_vars: Optional global context variables
        
        Returns:
            AgentResponse with structured classification
        """
        if context_vars is None:
            context_vars = {}
        
        current_time = datetime.now()
        user_message = f"""Current datetime: {current_time.isoformat()}

User input: "{text}"
"""
        
        if context_vars:
            context_str = "\n".join([f"- {key}: {value}" for key, value in context_vars.items()])
            user_message += f"\nGlobal context:\n{context_str}\n"
        
        # Build messages with history
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        try:
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=AgentResponse,
            )
            
            agent_response = completion.choices[0].message.parsed
            return agent_response
            
        except Exception as e:
            traceback.print_exc()
            return AgentResponse(
                intent='NOTE',
                content=text,
                category='Uncategorized',
                due_date=None,
                is_complete=False,
                clarification_question="I encountered an error processing your request. Could you please rephrase?"
            )
    
    async def get_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for text using OpenAI text-embedding-3-small
        """
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            traceback.print_exc()
            return []

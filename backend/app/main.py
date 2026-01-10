"""
FastAPI Entry Point
Voice Agent Application Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import voice, notes, reminders, agent, admin

# Load environment variables from .env file


app = FastAPI(
    title="Voice Agent API",
    description="Backend API for Voice Agent Application",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(voice.router)
app.include_router(notes.router)
app.include_router(reminders.router)
app.include_router(agent.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "Voice Agent API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


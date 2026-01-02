# Voice Agent App - AI Coding Assistant Instructions

## Architecture Overview

**Voice-powered note-taking app** with FastAPI backend, React frontend, and Supabase database.

### Key Components
- **Backend**: FastAPI at [backend/app/main.py](backend/app/main.py) with routers (voice, notes, reminders) and services (voice_service, llm_service, database_service)
- **Frontend**: React + Vite with hooks for audio recording (`useAudioRecording.js`) and auth (`useAuth.js`)
- **Database**: Supabase with pgvector extension for semantic search. Schema at [supabase/migrations/001_initial_schema.sql](supabase/migrations/001_initial_schema.sql)

### Data Flow
1. Voice input → Frontend audio capture → Backend `/api/voice/transcribe`
2. VoiceService uses OpenAI Whisper for transcription
3. LLMService processes intent (NOTE/REMINDER) - currently stubbed
4. DatabaseService stores to Supabase with RLS (Row-Level Security)
5. Vector embeddings enable semantic search (pgvector with 1536 dimensions)

## Critical Conventions

### Backend Patterns
- **Service Pattern**: Each router uses a dedicated service class (e.g., [voice.py](backend/app/routers/voice.py) → `VoiceService`)
- **Config**: All settings via `Settings` class in [core/config.py](backend/app/core/config.py) using `pydantic_settings`
- **Schemas**: Pydantic models in [models/schemas.py](backend/app/models/schemas.py) - use `Config.from_attributes = True` for ORM compatibility
- **Database**: `DatabaseService` has TWO clients:
  - `get_client()`: Uses `SUPABASE_ANON_KEY`, subject to RLS (user operations)
  - `get_service_client()`: Uses `SUPABASE_SERVICE_KEY`, bypasses RLS (admin operations)

### Frontend Patterns
- **API Client**: Axios instance in [services/api.js](frontend/src/services/api.js) with interceptors for auth tokens (TODO: implement)
- **Supabase Auth**: Direct Supabase client in [services/supabase.js](frontend/src/services/supabase.js) for authentication
- **Environment**: Vite uses `import.meta.env.VITE_*` prefix for env vars

### Database Schema
- **entries**: Main content table with `intent` enum (NOTE/REMINDER), `embedding` vector(1536), user_id FK to profiles
- **reminders**: Linked to entries via `entry_id`, has `due_date` and `status` enum
- **RLS Policies**: ALL tables have RLS enabled. Users can only access their own data via `auth.uid() = user_id`

## Development Commands

### Backend
This project uses [uv](https://github.com/astral-sh/uv) for Python package management.

```bash
cd backend
uv venv  # Create virtual environment
.venv\Scripts\activate  # Windows
uv run uvicorn app.main:app --reload  # Runs on :8000
```

**Without uv** (fallback):
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # Runs on :5173
```

### Database
- Migrations in [supabase/migrations/](supabase/migrations/) - apply via Supabase CLI or dashboard
- Vector search function at [002_vector_search_function.sql](supabase/migrations/002_vector_search_function.sql)

## Key Implementation Notes

### Audio Processing
- [VoiceService.transcribe_audio()](backend/app/services/voice_service.py#L18): Reads file into memory, passes to OpenAI Whisper as tuple `(filename, audio_content, content_type)`
- Frontend sends FormData with `multipart/form-data`

### TODO Areas (Incomplete Features)
- LLMService: Intent extraction and command processing logic stubbed
- Auth: Token interceptor in [api.js](frontend/src/services/api.js#L13) not implemented (backend trusts Supabase auth entirely)
- Routers: notes.py and reminders.py have placeholder endpoints without database integration
- Vector search: Function exists in SQL but not exposed via API (when implementing, call via `rpc('search_entries', params)`)

### Environment Variables
**Backend** (.env):
- `OPENAI_API_KEY` - Required for Whisper transcription
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` - Required for database
- `SUPABASE_SERVICE_KEY` - Optional, needed for admin operations

**Frontend** (.env.local):
- `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` - Supabase auth
- `VITE_API_BASE_URL` - Backend API (default: http://localhost:8000)

## When Implementing Features

1. **Adding Endpoints**: Create router → service class → update [main.py](backend/app/main.py) to include router
2. **Database Operations**: Always use `DatabaseService` methods. Check if operation needs service_client (bypasses RLS)
3. **New Schemas**: Add to [schemas.py](backend/app/models/schemas.py) with proper Pydantic config
4. **Vector Operations**: Embeddings are 1536-dimensional (OpenAI text-embedding-ada-002 format)
5. **Auth**: Frontend manages sessions via Supabase client. Backend trusts Supabase RLS policies - no JWT validation needed

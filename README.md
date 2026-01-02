# Voice Agent App

A voice-powered note-taking and reminder application built with FastAPI, React, and Supabase.

## Features

- 🎤 Voice recording and transcription
- 📝 Note creation and management
- ⏰ Reminder creation and tracking
- 🔐 User authentication
- 📱 Progressive Web App (PWA) support

## Project Structure

```
voice_agent_app/
├── backend/                # FastAPI Application
│   ├── app/
│   │   ├── main.py         # Entry point
│   │   ├── routers/         # API endpoints (voice, notes, reminders)
│   │   ├── services/       # Logic for LLM, STT, and Database
│   │   ├── models/         # Pydantic schemas
│   │   └── core/           # Config and Security
│   ├── requirements.txt
│   └── .env                # API Keys (OpenAI, Supabase)
├── frontend/               # React (Vite) Application
│   ├── src/
│   │   ├── components/     # UI: Pulse button, Dashboard cards
│   │   ├── hooks/          # Audio recording, Auth hooks
│   │   ├── services/       # API client (Axios/Supabase)
│   │   └── App.jsx
│   ├── public/             # Manifest for PWA
│   └── .env.local          # Supabase URL/Anon Key
├── supabase/               # SQL Migrations and Seed data
│   └── migrations/
└── README.md
```

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env` and fill in your API keys:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `SUPABASE_URL`: Your Supabase project URL
     - `SUPABASE_ANON_KEY`: Your Supabase anonymous key
     - `SUPABASE_SERVICE_KEY`: Your Supabase service role key (optional)

5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   - Copy `.env.local` and fill in your Supabase credentials:
     - `VITE_SUPABASE_URL`: Your Supabase project URL
     - `VITE_SUPABASE_ANON_KEY`: Your Supabase anonymous key
     - `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

4. Run the development server:
   ```bash
   npm run dev
   ```

The app will be available at `http://localhost:5173`

### Supabase Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)

2. Run migrations:
   - Create your database tables using SQL migrations in `supabase/migrations/`

3. Configure authentication:
   - Set up email/password authentication in Supabase dashboard
   - Configure any additional auth providers as needed

## Development

### Backend API Endpoints

- `GET /` - API root
- `GET /health` - Health check
- `POST /api/voice/transcribe` - Transcribe audio
- `POST /api/voice/process` - Process voice command
- `GET /api/notes` - Get all notes
- `POST /api/notes` - Create a note
- `GET /api/notes/{id}` - Get a note
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note
- `GET /api/reminders` - Get all reminders
- `POST /api/reminders` - Create a reminder
- `GET /api/reminders/{id}` - Get a reminder
- `PUT /api/reminders/{id}` - Update a reminder
- `DELETE /api/reminders/{id}` - Delete a reminder

### Frontend Components

- `PulseButton` - Voice recording button with pulse animation
- `DashboardCard` - Reusable card for displaying notes and reminders

### Hooks

- `useAudioRecording` - Manages audio recording state
- `useAuth` - Manages authentication state

## Technologies

- **Backend**: FastAPI, Python, Supabase
- **Frontend**: React, Vite, Axios
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Voice**: OpenAI Whisper (STT)
- **LLM**: OpenAI GPT (for command processing)

## License

MIT


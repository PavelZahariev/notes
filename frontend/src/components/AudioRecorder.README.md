# AudioRecorder Component

A reusable React component for voice recording and transcription.

## Features

✅ **Click-to-Start/Stop Recording** - Simple button interface for easy debugging and control  
✅ **MIME Type Compatibility** - Automatically detects best audio format (webm for Chrome/Android, mp4 for iOS)  
✅ **Permission Handling** - Gracefully requests and manages microphone permissions  
✅ **Visual Feedback** - Shows recording timer, transcribing state, and pulse animation  
✅ **API Integration** - Posts audio to `/api/voice/transcribe` endpoint  
✅ **Error Handling** - Displays user-friendly error messages  
✅ **Transcription Display** - Shows the returned transcription text  

## Usage

```jsx
import AudioRecorder from './components/AudioRecorder'

function App() {
  return (
    <div>
      <AudioRecorder />
    </div>
  )
}
```

## How It Works

1. **Permission Request**: On first use, requests microphone permission
2. **Start Recording**: Click the button to start capturing audio
3. **Recording Timer**: Displays elapsed time (MM:SS format)
4. **Stop Recording**: Click again to stop and process
5. **Audio Processing**: 
   - Creates a Blob from recorded chunks
   - Determines file extension based on MIME type (webm/m4a/ogg/wav)
   - Creates FormData with the audio file
   - POSTs to backend `/api/voice/transcribe`
6. **Display Result**: Shows transcription text or error message

## MIME Type Selection

The component automatically selects the best supported audio format:

1. `audio/webm` (preferred for Chrome/Edge/Android)
2. `audio/webm;codecs=opus`
3. `audio/mp4` (iOS Safari)
4. `audio/ogg;codecs=opus`
5. `audio/wav` (fallback)

## Audio Settings

The component uses optimized audio constraints:
- Echo cancellation: enabled
- Noise suppression: enabled
- Auto gain control: enabled

## State Management

The component manages the following states:
- `isRecording` - Whether actively recording
- `isTranscribing` - Whether processing audio
- `recordingTime` - Elapsed recording time in seconds
- `permissionGranted` - Microphone permission status
- `transcription` - Returned transcription text
- `error` - Error message if something fails

## Styling

The component includes:
- Gradient pulse button with animation
- Recording timer display
- Loading spinner during transcription
- Styled transcription result box
- Error message display
- Responsive design for mobile

## API Integration

Uses the `voiceAPI.transcribe()` method from `services/api.js`:

```javascript
const result = await voiceAPI.transcribe(audioFile)
// Returns: { text: "...", language: "en" }
```

## Testing

To test the component:

1. Start the backend: `cd backend && uv run uvicorn app.main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Navigate to http://localhost:5173
4. Click the microphone button and speak
5. Click again to stop and see transcription

## Troubleshooting

**No transcription returned**: Check that backend is running and OPENAI_API_KEY is set

**Permission denied**: User must manually enable microphone in browser settings

**Unsupported format**: Component will try multiple MIME types, but some browsers may have limited support

**Silent recording**: Check microphone is connected and not muted in system settings

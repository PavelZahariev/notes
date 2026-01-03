import { useState, useRef, useCallback, useEffect } from 'react'
import { voiceAPI } from '../services/api'
import './AudioRecorder.css'

/**
 * AudioRecorder Component
 * Captures voice input and sends it to the FastAPI process endpoint
 * which transcribes the audio and classifies the intent using the Agent service
 * 
 * Features:
 * - Click-to-start/stop recording
 * - MIME type compatibility (webm/mp4 fallback)
 * - Permission handling
 * - Visual feedback (recording/processing states)
 * - Displays agent response with intent, content, category, and due date
 */
function AudioRecorder() {
  // Recording state
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [permissionGranted, setPermissionGranted] = useState(null)
  
  // Results state
  const [agentResponse, setAgentResponse] = useState(null)
  const [error, setError] = useState(null)
  
  // Refs
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const streamRef = useRef(null)
  const timerRef = useRef(null)
  const mimeTypeRef = useRef('')

  /**
   * Get supported MIME type
   * Prefers audio/webm (Chrome/Android), falls back to audio/mp4 (iOS)
   */
  const getSupportedMimeType = useCallback(() => {
    const types = [
      'audio/webm',
      'audio/webm;codecs=opus',
      'audio/mp4',
      'audio/ogg;codecs=opus',
      'audio/wav',
    ]
    
    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        console.log(`Using MIME type: ${type}`)
        return type
      }
    }
    
    // Default fallback
    return ''
  }, [])

  /**
   * Request microphone permission
   */
  const requestPermission = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      setPermissionGranted(true)
      // Stop the stream immediately, we'll request it again when recording
      stream.getTracks().forEach(track => track.stop())
      return true
    } catch (err) {
      console.error('Permission denied:', err)
      setPermissionGranted(false)
      setError('Microphone permission denied. Please enable it in your browser settings.')
      return false
    }
  }, [])

  /**
   * Start recording
   */
  /**
   * Starts audio recording by requesting microphone permission, initializing MediaRecorder,
   * and setting up audio stream with echo cancellation and noise suppression.
   * Uses useCallback to memoize the function and prevent unnecessary re-creation on each render,
   * since it's only dependent on permissionGranted, requestPermission, and getSupportedMimeType.
   * This is particularly important when passed as a prop to child components or used in effect dependencies.
   * 
   * @async
   * @function startRecording
   * @returns {Promise<void>}
   * @throws {Error} When microphone access is denied or MediaRecorder initialization fails
   * 
   * @description
   * - Resets error state and transcription
   * - Requests microphone permission if not already granted
   * - Creates audio stream with enhanced audio settings (echo cancellation, noise suppression, auto gain)
   * - Initializes MediaRecorder with browser-supported MIME type
   * - Collects audio chunks during recording
   * - Sends audio blob to backend when recording stops
   * - Manages recording timer that updates every second
   * - Properly cleans up media tracks on stop
   */
  const startRecording = useCallback(async () => {
    try {
      setError(null)
      setAgentResponse(null)
      
      // Request permission if not already granted
      if (permissionGranted === null) {
        const granted = await requestPermission()
        if (!granted) return
      }

      // Get audio stream
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      })
      streamRef.current = stream

      // Get supported MIME type
      const mimeType = getSupportedMimeType()
      mimeTypeRef.current = mimeType

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: mimeType || undefined,
      })
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      // Handle data available
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      // Handle stop
      mediaRecorder.onstop = async () => {
        const mimeType = mimeTypeRef.current || 'audio/webm'
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType })
        
        // Stop all tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
        }

        // Send to backend
        await sendToBackend(audioBlob, mimeType)
      }

      // Start recording
      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)

    } catch (err) {
      console.error('Failed to start recording:', err)
      setError(`Failed to start recording: ${err.message}`)
    }
  }, [permissionGranted, requestPermission, getSupportedMimeType])

  /**
   * Stop recording
   */
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      
      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [isRecording])

  /**
   * Send audio to backend for processing (transcription + intent classification)
   */
  const sendToBackend = async (audioBlob, mimeType) => {
    try {
      setIsTranscribing(true)
      setError(null)

      // Determine file extension
      const extension = mimeType.includes('mp4') ? 'm4a' : 
                       mimeType.includes('ogg') ? 'ogg' :
                       mimeType.includes('wav') ? 'wav' : 'webm'
      
      // Create file from blob
      const audioFile = new File(
        [audioBlob], 
        `recording.${extension}`, 
        { type: mimeType }
      )

      console.log(`Sending ${audioFile.size} bytes to backend (${mimeType})`)

      // Call process API (transcribe + classify)
      const result = await voiceAPI.process(audioFile)
      
      console.log('Agent response:', result)
      setAgentResponse(result)

    } catch (err) {
      console.error('Processing failed:', err)
      setError(`Processing failed: ${err.response?.data?.detail || err.message}`)
    } finally {
      setIsTranscribing(false)
    }
  }

  /**
   * Handle button click
   */
  const handleButtonClick = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  /**
   * Format time as MM:SS
   */
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, []) 

  return (
    <div className="audio-recorder">
      {/* Recording Button */}
      <div className="recorder-controls">
        <button
          className={`record-button ${isRecording ? 'recording' : ''} ${isTranscribing ? 'disabled' : ''}`}
          onClick={handleButtonClick}
          disabled={isTranscribing}
          aria-label={isRecording ? 'Stop recording' : 'Start recording'}
        >
          <span className="button-icon">🎤</span>
          {isRecording && <span className="pulse-ring"></span>}
        </button>
        
        {/* Status Label */}
        <p className="status-label">
          {isRecording && `Recording... ${formatTime(recordingTime)}`}
          {!isRecording && !isTranscribing && 'Click to record'}
          {isTranscribing && 'Processing...'}
        </p>
      </div>

      {/* Loading Indicator */}
      {isTranscribing && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Processing your voice...</p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <p>{error}</p>
        </div>
      )}

      {/* Agent Response Result */}
      {agentResponse && !isTranscribing && (
        <div className="transcription-result">
          <h3>Response:</h3>
          <div className="agent-response">
            <div className="response-field">
              <span className="field-label">Intent:</span>
              <span className={`intent-badge intent-${agentResponse.intent?.toLowerCase()}`}>
                {agentResponse.intent}
              </span>
            </div>
            <div className="response-field">
              <span className="field-label">Content:</span>
              <p className="transcription-text">{agentResponse.content}</p>
            </div>
            <div className="response-field">
              <span className="field-label">Category:</span>
              <span className="category-badge">{agentResponse.category}</span>
            </div>
            {agentResponse.due_date && (
              <div className="response-field">
                <span className="field-label">Due Date:</span>
                <span className="due-date">{new Date(agentResponse.due_date).toLocaleString()}</span>
              </div>
            )}
            {!agentResponse.is_complete && agentResponse.clarification_question && (
              <div className="response-field clarification">
                <span className="field-label">⚠️ Clarification needed:</span>
                <p className="clarification-text">{agentResponse.clarification_question}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Permission Status */}
      {permissionGranted === false && (
        <button 
          className="permission-button"
          onClick={requestPermission}
        >
          Grant Microphone Permission
        </button>
      )}
    </div>
  )
}

export default AudioRecorder

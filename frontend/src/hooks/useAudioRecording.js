import { useState, useRef, useCallback } from 'react'

/**
 * useAudioRecording Hook
 * Manages audio recording state and functionality
 */
function useAudioRecording() {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [error, setError] = useState(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setError(null)
    } catch (err) {
      setError('Failed to start recording: ' + err.message)
      console.error('Recording error:', err)
    }
  }, [])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }, [isRecording])

  const resetRecording = useCallback(() => {
    setAudioBlob(null)
    setError(null)
    audioChunksRef.current = []
  }, [])

  return {
    isRecording,
    audioBlob,
    error,
    startRecording,
    stopRecording,
    resetRecording
  }
}

export default useAudioRecording


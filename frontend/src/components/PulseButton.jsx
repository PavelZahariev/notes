import { useState, useRef, useEffect } from 'react'
import './PulseButton.css'

/**
 * PulseButton Component
 * Voice recording button with pulse animation
 */
function PulseButton({ onStartRecording, onStopRecording, isRecording }) {
  const buttonRef = useRef(null)

  const handleClick = () => {
    if (isRecording) {
      onStopRecording()
    } else {
      onStartRecording()
    }
  }

  return (
    <div className="pulse-button-container">
      <button
        ref={buttonRef}
        className={`pulse-button ${isRecording ? 'recording' : ''}`}
        onClick={handleClick}
        aria-label={isRecording ? 'Stop recording' : 'Start recording'}
      >
        <span className="pulse-button-icon">🎤</span>
        {isRecording && <span className="pulse-ring"></span>}
      </button>
      <p className="pulse-button-label">
        {isRecording ? 'Recording...' : 'Tap to record'}
      </p>
    </div>
  )
}

export default PulseButton


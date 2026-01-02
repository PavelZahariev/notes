import { useState } from 'react'
import './App.css'
import AudioRecorder from './components/AudioRecorder'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <header className="App-header">
        <h1>Voice Agent App</h1>
        <p>Voice-powered note-taking and reminders</p>
      </header>
      
      <main className="App-main">
        <AudioRecorder />
      </main>
    </div>
  )
}

export default App


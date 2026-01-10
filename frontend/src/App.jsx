import { useState } from 'react'
import './App.css'
import AudioRecorder from './components/AudioRecorder'
import LoginForm from './components/LoginForm'
import { AuthProvider, useAuth } from './context/AuthContext'

function AppContent() {
  const { user, signOut } = useAuth();

  if (!user) {
    return <LoginForm />;
  }

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-top">
          <h1>Voice Agent App</h1>
          <button onClick={signOut} className="sign-out-btn">Sign Out</button>
        </div>
        <p>Voice-powered note-taking and reminders</p>
      </header>

      <main className="App-main">
        <AudioRecorder />
      </main>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App


import React, { useState } from 'react'
import ConversationalChat from './components/ConversationalChat'
import AIAvatar from './components/AIAvatar'
import LeadForm from './components/LeadForm'
import './App.css'

function App() {
  const [showLeadForm, setShowLeadForm] = useState(false)
  const [isAvatarTyping, setIsAvatarTyping] = useState(false)
  const [isAvatarSpeaking, setIsAvatarSpeaking] = useState(false)

  const handleShowLeadForm = () => {
    setShowLeadForm(true)
  }

  const handleCloseLeadForm = () => {
    setShowLeadForm(false)
  }

  const handleLeadSubmit = (leadData) => {
    console.log('Lead submitted:', leadData)
    setShowLeadForm(false)
    // Handle lead submission logic here
  }

  const handleAvatarStateChange = (typing, speaking) => {
    setIsAvatarTyping(typing)
    setIsAvatarSpeaking(speaking)
  }

  return (
    <div className="app">
      <div className="app-background">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>
      
      <header className="app-header">
        <div className="header-content">
          <div className="brand">
            <span className="flag-icon">🇺🇸</span>
            <h1>World Immigration Consultant</h1>
          </div>
        </div>
      </header>
      
      <main className="app-main">
        <AIAvatar 
          isTyping={isAvatarTyping}
          isSpeaking={isAvatarSpeaking}
        />
        
        <div className="consultation-container">
          <ConversationalChat 
            onShowLeadForm={handleShowLeadForm}
            onAvatarStateChange={handleAvatarStateChange}
          />
        </div>
      </main>
      
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-links">
            <span>© 2024 World Immigration Consultant</span>
            <span>•</span>
            <span>Privacy Policy</span>
            <span>•</span>
            <span>Terms of Service</span>
          </div>
        </div>
      </footer>

      {showLeadForm && (
        <div className="lead-form-overlay">
          <LeadForm 
            onSubmit={handleLeadSubmit}
            onClose={handleCloseLeadForm}
          />
        </div>
      )}
    </div>
  )
}

export default App 
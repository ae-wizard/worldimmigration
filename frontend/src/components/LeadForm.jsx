import { useState } from 'react'
import './LeadForm.css'

function LeadForm({ onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    current_country: '',
    goal: '',
    timeline: '',
    additional_info: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const countries = [
    'India', 'China', 'Mexico', 'Philippines', 'Vietnam', 'Nigeria', 'Brazil', 'Canada',
    'United Kingdom', 'Germany', 'France', 'Australia', 'Japan', 'South Korea', 'Other'
  ]

  const goalOptions = [
    'Work in the US',
    'Study in the US', 
    'Join family in US',
    'Visit/Tourism',
    'Get Green Card',
    'Become US Citizen',
    'Invest in US',
    'Other'
  ]

  const timelineOptions = [
    'As soon as possible',
    'Within 6 months',
    '6-12 months',
    '1-2 years',
    '2+ years',
    'Just exploring options'
  ]

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const response = await fetch('http://localhost:8000/lead', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        setIsSubmitted(true)
        setTimeout(() => {
          onClose()
        }, 3000)
      } else {
        throw new Error('Failed to submit lead')
      }
    } catch (error) {
      console.error('Error submitting lead:', error)
      alert('Sorry, there was an error submitting your information. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <div className="lead-form-overlay">
        <div className="lead-form">
          <div className="success-message">
            <div className="success-icon">✅</div>
            <h3>Thank you!</h3>
            <p>We've received your information and will contact you within 24 hours to discuss your immigration goals and next steps.</p>
            <p><strong>What happens next:</strong></p>
            <ul style={{ textAlign: 'left', margin: '1rem 0' }}>
              <li>Review of your specific situation</li>
              <li>Personalized consultation call</li>
              <li>Custom immigration strategy</li>
              <li>Timeline and cost estimate</li>
            </ul>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="lead-form-overlay">
      <div className="lead-form">
        <div className="form-header">
          <h3>🎯 Get Expert Immigration Consultation</h3>
          <p>Schedule a free consultation with our immigration specialists to create your personalized pathway to the US.</p>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="form-content">
          <div className="form-group">
            <label htmlFor="name">Name *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Your Name"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="your.email@example.com"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone Number (Optional)</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+1 (555) 123-4567"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="current_country">Country of Origin *</label>
            <select
              id="current_country"
              name="current_country"
              value={formData.current_country}
              onChange={handleChange}
              required
              className="form-select"
            >
              <option value="">Select your country</option>
              {countries.map(country => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="goal">Immigration Goal *</label>
            <select
              id="goal"
              name="goal"
              value={formData.goal}
              onChange={handleChange}
              required
              className="form-select"
            >
              <option value="">Select your goal</option>
              {goalOptions.map(goal => (
                <option key={goal} value={goal}>{goal}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="timeline">Desired Timeline</label>
            <select
              id="timeline"
              name="timeline"
              value={formData.timeline}
              onChange={handleChange}
              className="form-select"
            >
              <option value="">Select timeline</option>
              {timelineOptions.map(timeline => (
                <option key={timeline} value={timeline}>{timeline}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="additional_info">Additional Information</label>
            <textarea
              id="additional_info"
              name="additional_info"
              value={formData.additional_info}
              onChange={handleChange}
              placeholder="Any specific questions, concerns, or details about your situation..."
              rows="3"
              className="form-textarea"
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={onClose}
              className="cancel-button"
              disabled={isSubmitting}
            >
              Maybe Later
            </button>
            <button
              type="submit"
              className="submit-button"
              disabled={!formData.name || !formData.email || !formData.current_country || !formData.goal || isSubmitting}
            >
              {isSubmitting ? 'Submitting...' : 'Get Free Consultation 🚀'}
            </button>
          </div>
        </form>

        <div className="form-footer">
          <p>
            <small>
              🔒 Your information is secure and confidential. We'll only use it to provide 
              immigration assistance and will never share it with third parties.
            </small>
          </p>
        </div>
      </div>
    </div>
  )
}

export default LeadForm 
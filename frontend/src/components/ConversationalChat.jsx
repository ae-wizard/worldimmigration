import React, { useState, useRef, useEffect } from 'react';
import './ConversationalChat.css';

// Global flag to prevent React.StrictMode double initialization
let globalConversationStarted = false;

const ConversationalChat = ({ onShowLeadForm, onAvatarStateChange, showAvatar = true }) => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [currentStep, setCurrentStep] = useState('welcome');
  const [userProfile, setUserProfile] = useState({});
  const [waitingForUser, setWaitingForUser] = useState(false);
  const [showInputField, setShowInputField] = useState(false);
  const [inputPlaceholder, setInputPlaceholder] = useState('');
  const conversationStartedRef = useRef(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // Sync typing state with avatar
  useEffect(() => {
    if (onAvatarStateChange) {
      onAvatarStateChange(isTyping, false);
    }
  }, [isTyping, onAvatarStateChange]);

  // ONE-TIME initialization that survives React.StrictMode
  useEffect(() => {
    if (!globalConversationStarted && !conversationStartedRef.current) {
      globalConversationStarted = true;
      conversationStartedRef.current = true;
      console.log('Starting conversation (StrictMode-safe)');
      
      setTimeout(() => {
        startConversation();
      }, 1500);
    }
  }, []);

  // Debug log for waitingForUser state
  useEffect(() => {
    console.log('waitingForUser changed to:', waitingForUser);
  }, [waitingForUser]);

  const conversationFlow = {
    welcome: {
      message: "Hello! I'm Sarah, your personal immigration consultant. I'm here to help you navigate U.S. immigration - completely free.",
      nextMessage: "I use the latest USCIS data, updated every hour, to give you the most current guidance. Let's start - what country are you from?",
      inputType: "select",
      placeholder: "Select your country",
      options: [
        { text: "India", value: "from_india" },
        { text: "China", value: "from_china" },
        { text: "Mexico", value: "from_mexico" },
        { text: "Canada", value: "from_canada" },
        { text: "United Kingdom", value: "from_uk" },
        { text: "Germany", value: "from_germany" },
        { text: "Philippines", value: "from_philippines" },
        { text: "Brazil", value: "from_brazil" },
        { text: "Nigeria", value: "from_nigeria" },
        { text: "Peru", value: "from_peru" },
        { text: "South Korea", value: "from_south_korea" },
        { text: "Japan", value: "from_japan" },
        { text: "Australia", value: "from_australia" },
        { text: "Other country", value: "from_other" }
      ]
    },
    from_india: {
      message: "Perfect! India is one of the largest sources of U.S. immigrants. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_china: {
      message: "Great! China has many pathways to U.S. immigration. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_mexico: {
      message: "Excellent! Mexico has special programs and pathways. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_canada: {
      message: "Wonderful! Canadians have some streamlined processes. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_uk: {
      message: "Great choice! UK citizens have various pathways available. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_germany: {
      message: "Perfect! Germany has strong ties with U.S. immigration programs. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_philippines: {
      message: "Excellent! The Philippines has established immigration pathways. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_brazil: {
      message: "Great! Brazil has growing opportunities for U.S. immigration. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_nigeria: {
      message: "Perfect! Nigeria has increasing immigration success stories. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_peru: {
      message: "Excellent! Peru has good relationships with U.S. immigration programs. What type of visa are you interested in?",
      followUp: "visa_types"
    },
    from_other: {
      message: "Please tell me which country you're from:",
      inputType: "text",
      placeholder: "Enter your country of citizenship...",
      followUp: "visa_types"
    },
    visa_types: {
      message: "Here are the main U.S. visa categories. Which one interests you most?",
      inputType: "select",
      placeholder: "Select visa type",
      options: [
        { text: "Work visas (H1B, L1, O1)", value: "work_visas" },
        { text: "Student visas (F1, M1)", value: "student_visas" },
        { text: "Family-based Green Cards", value: "family_green_card" },
        { text: "Employment Green Cards", value: "employment_green_card" },
        { text: "Investment visas (EB5)", value: "investment_visas" },
        { text: "Tourist/Business (B1/B2)", value: "tourist_business" },
        { text: "Other visa types", value: "other_visas" }
      ]
    },
    work_visas: {
      message: "Work visas are popular! Let me give you specific guidance based on your background.",
      options: [
        { text: "I have a job offer", value: "has_job_offer", icon: "✅" },
        { text: "Looking for work", value: "seeking_job", icon: "🔍" },
        { text: "Self-employed/Business", value: "self_employed", icon: "🚀" },
        { text: "Intra-company transfer", value: "l1_transfer", icon: "🏢" }
      ]
    },
    student_visas: {
      message: "Student visas are a great pathway! What's your education goal?",
      options: [
        { text: "Bachelor's degree", value: "bachelors_study", icon: "🎓" },
        { text: "Master's degree", value: "masters_study", icon: "📚" },
        { text: "PhD/Doctorate", value: "phd_study", icon: "🔬" },
        { text: "Vocational training", value: "vocational_study", icon: "🔧" }
      ]
    },
    employment_green_card: {
      message: "Employment-based Green Cards are excellent for permanent residence! What's your situation?",
      options: [
        { text: "I have a job offer", value: "has_job_offer", icon: "✅" },
        { text: "Extraordinary ability", value: "extraordinary_ability", icon: "⭐" },
        { text: "Advanced degree", value: "advanced_degree", icon: "🎓" },
        { text: "Skilled worker", value: "skilled_worker", icon: "💼" }
      ]
    },
    has_job_offer: {
      message: "Excellent! Having a job offer gives you strong options. What's your education level?",
      options: [
        { text: "Bachelor's degree or higher", value: "bachelors_plus", icon: "🎓" },
        { text: "Some college", value: "some_college", icon: "📚" },
        { text: "High school", value: "high_school", icon: "🏫" }
      ]
    },
    seeking_job: {
      message: "I can help you understand what employers look for and visa requirements. What's your field?",
      options: [
        { text: "Technology/Engineering", value: "tech_field", icon: "💻" },
        { text: "Healthcare/Medicine", value: "healthcare_field", icon: "🏥" },
        { text: "Business/Finance", value: "business_field", icon: "💰" },
        { text: "Research/Academia", value: "research_field", icon: "🔬" },
        { text: "Other field", value: "other_field", icon: "💼" }
      ]
    }
  };

  const addMessage = (text, isUser = false, hasOptions = false, options = null, inputType = null, placeholder = null) => {
    const newMessage = {
      id: Date.now() + Math.random(),
      text,
      isUser,
      hasOptions,
      options,
      inputType,
      placeholder,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  };

  const simulateTyping = async (delay = 1000) => {
    setIsTyping(true);
    await new Promise(resolve => setTimeout(resolve, delay));
    setIsTyping(false);
  };

  const handleUserChoice = async (choice) => {
    console.log('User chose:', choice, 'Current waitingForUser:', waitingForUser);
    
    // Disable waiting state immediately to prevent double clicks
    setWaitingForUser(false);
    
    // Find the selected option text for display
    const lastMessage = messages[messages.length - 1];
    let selectedOptionText = choice;
    
    if (lastMessage?.options) {
      const selectedOption = lastMessage.options.find(opt => opt.value === choice);
      if (selectedOption) {
        selectedOptionText = selectedOption.text;
      }
    }
    
    addMessage(selectedOptionText, true);

    // Save user choice
    setUserProfile(prev => ({
      ...prev,
      [currentStep]: choice
    }));

    await simulateTyping(800);

    // Navigate to next step
    const flowStep = conversationFlow[choice];
    
    if (flowStep) {
      // Add Sarah's response
      addMessage(flowStep.message);
      
      // Add follow-up message if exists
      if (flowStep.nextMessage) {
        await simulateTyping(1500);
        addMessage(flowStep.nextMessage);
      }

      // Handle next options or input
      if (flowStep.options) {
        await simulateTyping(500);
        addMessage("", false, true, flowStep.options, flowStep.inputType, flowStep.placeholder);
        setWaitingForUser(true);
      } else if (flowStep.inputType === 'text') {
        setShowInputField(true);
        setInputPlaceholder(flowStep.placeholder || 'Type your response...');
        setWaitingForUser(true);
      } else if (flowStep.followUp) {
        // Auto-advance to follow-up step
        setCurrentStep(flowStep.followUp);
        await simulateTyping(1000);
        const nextStep = conversationFlow[flowStep.followUp];
        if (nextStep) {
          addMessage(nextStep.message);
          if (nextStep.options) {
            await simulateTyping(500);
            addMessage("", false, true, nextStep.options, nextStep.inputType, nextStep.placeholder);
            setWaitingForUser(true);
          }
        }
        return;
      }
      
      setCurrentStep(choice);
    } else {
      // Handle responses based on what was gathered
      await handlePersonalizedResponse(choice);
    }
  };

  const handlePersonalizedResponse = async (choice) => {
    if (choice === 'bachelors_plus') {
      addMessage("Perfect! With a bachelor's degree and a job offer, you're well-positioned for an H1B visa. The process typically takes 6-8 months.");
      await simulateTyping(1500);
      addMessage("Key steps: 1) Employer files H1B petition 2) Wait for approval 3) Apply for visa at consulate. Would you like me to explain any of these steps in detail?");
      
      await simulateTyping(500);
      addMessage("", false, true, [
        { text: "Explain the H1B process", value: "h1b_process", icon: "📋" },
        { text: "Timeline and costs", value: "h1b_timeline", icon: "⏰" },
        { text: "I have other questions", value: "free_questions", icon: "❓" }
      ]);
      setWaitingForUser(true);
      
    } else if (choice === 'tech_field') {
      addMessage("Technology professionals from China have excellent opportunities! With current demand for tech talent, you have several visa paths.");
      await simulateTyping(1500);
      addMessage("Your best options are likely H1B for specialty positions or L1 if transferring from a Chinese office. What specific role is your job offer for?");
      
      setShowInputField(true);
      setInputPlaceholder("Describe your job role (e.g., Software Engineer, Data Scientist)...");
      setWaitingForUser(true);
      
    } else if (choice === 'work_to_green_card') {
      addMessage("Excellent goal! The path from work visa to Green Card typically involves your employer sponsoring you for permanent residence.");
      await simulateTyping(1500);
      addMessage("This usually takes 1-3 years depending on your country of birth and the specific process. What type of work visa do you currently have?");
      
      setShowInputField(true);
      setInputPlaceholder("e.g., H1B, L1, O1, etc.");
      setWaitingForUser(true);
      
    } else if (choice === 'extend_work_visa') {
      addMessage("Work visa extensions are common and usually straightforward if you meet the requirements.");
      await simulateTyping(1500);
      addMessage("The process varies by visa type. What work visa are you currently on?");
      
      setShowInputField(true);
      setInputPlaceholder("e.g., H1B, L1, O1, etc.");
      setWaitingForUser(true);
      
    } else if (choice === 'citizenship') {
      addMessage("That's exciting! To apply for U.S. citizenship, you generally need to have been a permanent resident for at least 5 years (or 3 years if married to a U.S. citizen).");
      await simulateTyping(1500);
      addMessage("How long have you had your Green Card?");
      
      setShowInputField(true);
      setInputPlaceholder("e.g., 2 years, 5 years, etc.");
      setWaitingForUser(true);
      
    } else if (choice === 'student_to_h1b') {
      addMessage("Great choice! The F-1 to H1B path is very common. You'll typically use OPT first, then your employer can sponsor you for H1B.");
      await simulateTyping(1500);
      addMessage("Do you have a job offer or are you still looking?");
      
      await simulateTyping(500);
      addMessage("", false, true, [
        { text: "I have a job offer", value: "has_job_offer", icon: "✅" },
        { text: "Still looking for work", value: "seeking_job", icon: "🔍" },
        { text: "Currently on OPT", value: "on_opt", icon: "💼" }
      ]);
      setWaitingForUser(true);
      
    } else if (choice === 'free_questions') {
      addMessage("Great! I'm here to answer any immigration questions you have. What would you like to know?");
      setShowInputField(true);
      setInputPlaceholder("Ask me anything about immigration...");
      setWaitingForUser(true);
    } else if (choice === 'h1b_process') {
      addMessage("The H1B process has 3 main phases:");
      await simulateTyping(1000);
      addMessage("1. **Employer files petition** (March-April) - Your employer submits Form I-129 with supporting documents");
      await simulateTyping(1200);
      addMessage("2. **USCIS processing** (April-September) - Wait for petition approval, premium processing available for faster results");
      await simulateTyping(1200);
      addMessage("3. **Visa application** (After approval) - Apply at U.S. consulate in your country");
      
      await simulateTyping(800);
      addMessage("", false, true, [
        { text: "What documents do I need?", value: "h1b_documents", icon: "📄" },
        { text: "How much does it cost?", value: "h1b_timeline", icon: "💰" },
        { text: "Get my personalized plan", value: "get_assessment", icon: "📋" }
      ]);
      setWaitingForUser(true);
    } else if (choice === 'get_assessment') {
      addMessage("I'd love to prepare a detailed assessment for you! To provide the most accurate guidance, I'll need to connect you with our assessment team.");
      await simulateTyping(1500);
      addMessage("This will give you a personalized roadmap with timelines, costs, and next steps specific to your situation.");
      
      if (onShowLeadForm) {
        setTimeout(() => {
          onShowLeadForm();
        }, 1000);
      }
    } else {
      // Default response for unhandled choices
      addMessage("Thank you for that information! Let me provide you with some guidance based on your situation.");
      await simulateTyping(1500);
      addMessage("Every immigration case is unique. I'd recommend getting a personalized assessment to give you the most accurate guidance for your specific situation.");
      
      await simulateTyping(500);
      addMessage("", false, true, [
        { text: "Get personalized assessment", value: "get_assessment", icon: "📋" },
        { text: "I have more questions", value: "free_questions", icon: "❓" }
      ]);
      setWaitingForUser(true);
    }
  };

  const handleTextInput = async (text) => {
    addMessage(text, true);
    setShowInputField(false);
    setUserProfile(prev => ({
      ...prev,
      [currentStep + '_input']: text
    }));

    await simulateTyping(1000);
    
    if (currentStep === 'from_other') {
      addMessage(`Thank you! As someone from ${text}, let me provide specific guidance for your situation.`);
      await simulateTyping(1500);
      
      // Flow to visa types
      setCurrentStep('visa_types');
      const visaTypesStep = conversationFlow.visa_types;
      addMessage(visaTypesStep.message);
      await simulateTyping(500);
      addMessage("", false, true, visaTypesStep.options, visaTypesStep.inputType, visaTypesStep.placeholder);
      setWaitingForUser(true);
      
    } else {
      // Provide specific answers based on user question and profile
      const question = text.toLowerCase();
      let response = "";
      
      // Determine user's context from profile
      const country = Object.keys(userProfile).find(key => key.startsWith('from_'));
      const visaType = userProfile.visa_types || userProfile.family_green_card || userProfile.work_visas;
      
      if (question.includes('how long') || question.includes('timeline') || question.includes('time')) {
        if (visaType === 'family_green_card') {
          response = "Family-based Green Card processing times vary significantly:\n\n• **Immediate relatives** (spouse, unmarried children under 21, parents of US citizens): 8-12 months\n• **F1 category** (unmarried adult children of US citizens): 1-2 years\n• **F2A** (spouses/children of permanent residents): 2-3 years\n• **F3/F4** (siblings, married children): 10-20+ years\n\nProcessing also depends on your country - some countries have longer waits due to per-country limits.";
        } else if (visaType === 'work_visas') {
          response = "Work visa processing times:\n\n• **H1B**: 3-8 months (faster with premium processing)\n• **L1**: 2-4 months\n• **O1**: 2-3 months\n• **TN** (for Canadians/Mexicans): Same day at border\n\nEmployer petition filing + consular processing if outside US adds 2-3 months.";
        } else if (visaType === 'student_visas') {
          response = "Student visa processing:\n\n• **F1 visa application**: 2-8 weeks\n• **I-20 processing** by school: 2-4 weeks\n• **Consular interview**: 1-4 weeks wait time\n\nTotal timeline: 2-4 months from application to arrival in US.";
        } else {
          response = "Processing times depend on your specific visa type:\n\n• **Tourist visas**: 2-4 weeks\n• **Work visas**: 3-8 months\n• **Student visas**: 2-4 months\n• **Family Green Cards**: 8 months to 20+ years\n• **Employment Green Cards**: 1-5+ years\n\nI'd be happy to give you specific timelines once you share your visa goals!";
        }
      } else if (question.includes('cost') || question.includes('fee') || question.includes('money') || question.includes('expensive')) {
        response = "Immigration costs vary by visa type:\n\n**Work Visas:**\n• H1B: $2,000-$5,000 (employer pays most)\n• L1: $1,500-$3,000\n\n**Family Green Cards:**\n• $1,760 USCIS fees + $325 consular fees\n• Plus medical exam ($200-$500)\n\n**Student Visas:**\n• $160 visa fee + $350 SEVIS fee\n• Plus school costs\n\nAttorney fees typically add $2,000-$8,000 depending on complexity.";
      } else if (question.includes('document') || question.includes('paperwork') || question.includes('requirement')) {
        response = "Required documents typically include:\n\n**All visa types:**\n• Valid passport\n• Photos\n• Form DS-160 or equivalent\n• Financial support evidence\n\n**Work visas:** Employment letter, educational credentials\n**Family visas:** Marriage/birth certificates, sponsor's documents\n**Student visas:** I-20, acceptance letter, transcripts\n\nI can provide a specific checklist once you tell me your visa type!";
      } else if (question.includes('move') || question.includes('immigrate') || question.includes('live')) {
        response = "To move to the US permanently, your main options are:\n\n**1. Family-based Green Card** (if you have US citizen/resident relatives)\n**2. Employment-based Green Card** (through job offer)\n**3. Investment visa** (EB-5, $800K+ investment)\n**4. Diversity visa lottery** (if your country qualifies)\n\nMost people start with a temporary visa (work/student) then transition to permanent residence. What's your current situation?";
      } else {
        response = "That's a great question! Based on your interest in US immigration, here are some key points:\n\n• The path depends on your specific situation and goals\n• Most successful cases involve careful planning and proper documentation\n• Timeline and costs vary significantly by visa type\n• Having the right legal guidance makes a huge difference\n\nFor the most accurate advice, I'd recommend getting a personalized assessment based on your specific circumstances.";
      }
      
      addMessage(response);
      
      await simulateTyping(1000);
      addMessage("Do you have any other questions?", false, true, [
        { text: "Yes, I have more questions", value: "free_questions", icon: "❓" },
        { text: "Get my detailed assessment", value: "get_assessment", icon: "📋" }
      ]);
      setWaitingForUser(true);
    }
  };

  const startConversation = async () => {
    // StrictMode-safe check to prevent duplicates
    if (messages.length > 0 || !globalConversationStarted || !conversationStartedRef.current) {
      console.log('Conversation already started or not properly initialized, skipping...');
      return;
    }
    
    console.log('Starting conversation (final safety check passed)...');
    
    const welcomeStep = conversationFlow.welcome;
    
    // Add first message
    addMessage(welcomeStep.message);
    
    // Add second message after delay
    await simulateTyping(2000);
    addMessage(welcomeStep.nextMessage);
    
    // Add dropdown options after another delay
    await simulateTyping(1500);
    addMessage("", false, true, welcomeStep.options, welcomeStep.inputType, welcomeStep.placeholder);
    setWaitingForUser(true);
    
    console.log('Conversation started successfully');
  };

  return (
    <div className="conversational-chat">
      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.isUser ? 'user' : 'assistant'}`}>
            <div className="message-content">
              {message.text && (
                <div className="message-text">
                  {message.text}
                </div>
              )}
              
              {message.hasOptions && message.options && (
                <div className="message-options">
                  {message.inputType === 'select' ? (
                    <select
                      className="dropdown-select"
                      onChange={(e) => {
                        if (waitingForUser && e.target.value) {
                          handleUserChoice(e.target.value);
                        }
                      }}
                      disabled={!waitingForUser}
                      defaultValue=""
                    >
                      <option value="" disabled>{message.placeholder || "Select an option"}</option>
                      {message.options.map((option, index) => (
                        <option key={index} value={option.value}>
                          {option.text}
                        </option>
                      ))}
                    </select>
                  ) : (
                    message.options.map((option, index) => (
                      <button
                        key={index}
                        className={`option-button ${!waitingForUser ? 'disabled' : ''}`}
                        onClick={() => {
                          console.log('Button clicked:', option.value);
                          if (waitingForUser) {
                            handleUserChoice(option.value);
                          }
                        }}
                        disabled={!waitingForUser}
                      >
                        <span className="option-icon">{option.icon}</span>
                        <span className="option-text">{option.text}</span>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="message assistant">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        {showInputField && (
          <div className="text-input-container">
            <input
              type="text"
              placeholder={inputPlaceholder}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                  handleTextInput(e.target.value.trim());
                  e.target.value = '';
                }
              }}
              autoFocus
              className="text-input"
            />
            <button
              className="send-button"
              onClick={(e) => {
                const input = e.target.previousSibling;
                if (input.value.trim()) {
                  handleTextInput(input.value.trim());
                  input.value = '';
                }
              }}
            >
              Send
            </button>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ConversationalChat; 
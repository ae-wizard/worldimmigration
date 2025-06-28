# api_simple.py - Structured Immigration Consultant API
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import json
from typing import Optional, List
from db import init_db, log_conversation, create_lead

app = FastAPI(title="AI Immigration Consultant API - Guided Mode")

# Enable CORS for local dev and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",
        "https://worldimmigrationconsultant.com",
        "https://www.worldimmigrationconsultant.com",
        "https://beamish-marshmallow-c3f81a.netlify.app"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Structured visa information
VISA_TYPES = {
    "tourist": {
        "name": "Tourist/Visitor Visa (B-1/B-2)",
        "requirements": ["Valid passport", "Proof of funds", "Return ticket", "Ties to home country"],
        "processing_time": "2 weeks to 2 months",
        "info": "For temporary visits, tourism, or business meetings."
    },
    "work": {
        "name": "Work Visas (H-1B, L-1, O-1, etc.)",
        "requirements": ["Job offer from US employer", "Specialty occupation", "Bachelor's degree or equivalent"],
        "processing_time": "3-8 months",
        "info": "For employment in the United States."
    },
    "student": {
        "name": "Student Visa (F-1/M-1)",
        "requirements": ["Acceptance at US school", "Proof of funds", "Intent to return home"],
        "processing_time": "2-12 weeks",
        "info": "For academic or vocational studies."
    },
    "family": {
        "name": "Family-Based Immigration",
        "requirements": ["US citizen or permanent resident sponsor", "Approved petition", "Financial support"],
        "processing_time": "8 months to several years",
        "info": "For spouses, children, parents, or siblings of US citizens/residents."
    },
    "green_card": {
        "name": "Permanent Residence (Green Card)",
        "requirements": ["Approved petition", "Medical exam", "Background check", "Interview"],
        "processing_time": "1-3 years depending on category",
        "info": "For permanent residence in the United States."
    },
    "citizenship": {
        "name": "Naturalization/Citizenship",
        "requirements": ["5 years as permanent resident (3 if married to US citizen)", "English proficiency", "Civics test"],
        "processing_time": "10-13 months",
        "info": "To become a US citizen."
    }
}

COUNTRIES_SPECIAL_PROGRAMS = {
    "india": ["H-1B high demand", "EB-1/EB-2 backlog", "Premium processing available"],
    "china": ["EB-5 investment program", "EB-1/EB-2 backlog", "Student visa common"],
    "mexico": ["TN visa (NAFTA)", "Family immigration common", "Border proximity considerations"],
    "canada": ["TN visa (NAFTA)", "EB-1 for professionals", "Strong bilateral relations"],
    "philippines": ["Family immigration common", "Nursing/healthcare opportunities", "Military service considerations"],
    "vietnam": ["Family reunification", "Refugee programs", "Investment opportunities"],
    "nigeria": ["Student visas", "Diversity lottery", "Professional visas"],
    "brazil": ["E-2 investor visa", "Student exchange", "Tourism visa"],
}

class UserProfileRequest(BaseModel):
    current_country: str
    current_status: str  # "visitor", "student", "worker", "resident", "citizen", "none"
    goal: str  # "work", "study", "family", "invest", "visit", "permanent_residence", "citizenship"
    education_level: Optional[str] = None
    has_job_offer: Optional[bool] = None
    family_in_us: Optional[str] = None  # "spouse", "parent", "child", "sibling", "none"

class QuestionRequest(BaseModel):
    question: str
    user_profile: Optional[UserProfileRequest] = None

class LeadRequest(BaseModel):
    email: str
    phone: Optional[str] = None
    current_country: str
    goal: str
    timeline: Optional[str] = None
    additional_info: Optional[str] = None

def get_tailored_guidance(profile: UserProfileRequest) -> dict:
    """Generate tailored guidance based on user profile"""
    
    current_country = profile.current_country.lower()
    goal = profile.goal.lower()
    current_status = profile.current_status.lower()
    
    # Determine recommended visa type
    if goal == "work":
        if profile.has_job_offer:
            recommended_visa = "work"
            next_steps = [
                "Your employer should file H-1B or other work petition",
                "Prepare required documents (degree, experience letters)",
                "Consider premium processing for faster results"
            ]
        else:
            recommended_visa = None
            next_steps = [
                "Find a US employer willing to sponsor",
                "Use job sites like LinkedIn, Indeed, or company websites",
                "Consider EB-5 investment visa if you have $800K+ to invest"
            ]
    
    elif goal == "study":
        recommended_visa = "student"
        next_steps = [
            "Apply and get accepted to a US school",
            "Receive Form I-20 from the school",
            "Pay SEVIS fee and apply for F-1 visa",
            "Prepare for visa interview"
        ]
    
    elif goal == "family":
        recommended_visa = "family"
        if profile.family_in_us and profile.family_in_us != "none":
            next_steps = [
                f"Your {profile.family_in_us} should file Form I-130 petition",
                "Wait for petition approval",
                "Complete visa application when priority date is current",
                "Attend interview at US consulate"
            ]
        else:
            next_steps = [
                "You need a US citizen or permanent resident family member to sponsor you",
                "Eligible relationships: spouse, parent, child, or sibling",
                "Consider other immigration options if no family ties"
            ]
    
    elif goal == "permanent_residence":
        if current_status == "worker":
            recommended_visa = "green_card"
            next_steps = [
                "Ask employer to file I-140 petition",
                "File I-485 (if in US) or consular processing",
                "Consider EB-1 if you have extraordinary ability"
            ]
        elif current_status == "student":
            recommended_visa = "green_card"
            next_steps = [
                "Graduate and find employer sponsor",
                "Use OPT period to gain experience",
                "Have employer file for permanent residence"
            ]
        else:
            recommended_visa = "green_card"
            next_steps = [
                "Determine your eligibility category",
                "Family sponsorship, employment, or investment",
                "Consider EB-5 investor program ($800K minimum)"
            ]
    
    elif goal == "citizenship":
        if current_status == "resident":
            recommended_visa = "citizenship"
            next_steps = [
                "Ensure you meet residency requirements (5 years, or 3 if married to US citizen)",
                "Take citizenship test preparation course",
                "File Form N-400 application",
                "Attend naturalization interview"
            ]
        else:
            recommended_visa = None
            next_steps = [
                "You must first become a permanent resident",
                "Live as permanent resident for required time",
                "Then apply for citizenship"
            ]
    
    elif goal == "visit":
        recommended_visa = "tourist"
        next_steps = [
            "Apply for B-1/B-2 visitor visa",
            "Prepare documents showing ties to home country",
            "Demonstrate sufficient funds for trip",
            "Schedule visa interview"
        ]
    
    else:
        recommended_visa = None
        next_steps = ["Please clarify your immigration goal"]
    
    # Add country-specific advice
    country_advice = COUNTRIES_SPECIAL_PROGRAMS.get(current_country, [])
    
    return {
        "recommended_visa": recommended_visa,
        "next_steps": next_steps,
        "country_specific": country_advice,
        "estimated_timeline": VISA_TYPES[recommended_visa]["processing_time"] if recommended_visa else "Varies"
    }

@app.get("/")
async def root():
    return {"message": "AI Immigration Consultant API - Guided Mode", "status": "ready"}

@app.get("/visa-types")
async def get_visa_types():
    """Get all available visa types"""
    return {"visa_types": VISA_TYPES}

@app.post("/get-guidance")
async def get_guidance(profile: UserProfileRequest):
    """Get personalized immigration guidance based on user profile"""
    guidance = get_tailored_guidance(profile)
    
    # Log the consultation
    try:
        profile_summary = f"Country: {profile.current_country}, Status: {profile.current_status}, Goal: {profile.goal}"
        response_summary = f"Recommended: {guidance['recommended_visa']}, Timeline: {guidance['estimated_timeline']}"
        log_conversation(profile_summary, response_summary)
    except Exception as e:
        print(f"Error logging: {e}")
    
    return guidance

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    """Handle follow-up questions with context"""
    question = req.question.lower()
    
    # Determine response based on question content
    if any(word in question for word in ["cost", "fee", "price", "expensive"]):
        response = "💰 Immigration costs vary by case type:\n• Tourist visa: $160\n• Work visa (H-1B): $2,000-$5,000+\n• Green card: $3,000-$8,000+\n• Citizenship: $725\n\nNote: These are government fees only. Attorney fees are additional."
    
    elif any(word in question for word in ["time", "long", "wait", "processing"]):
        response = "⏱️ Processing times vary significantly:\n• Tourist visa: 2 weeks-2 months\n• Work visa: 3-8 months\n• Family immigration: 8 months-several years\n• Green card: 1-3 years\n• Citizenship: 10-13 months\n\nTimes depend on your country, case complexity, and current backlogs."
    
    elif any(word in question for word in ["interview", "appointment", "embassy"]):
        response = "🏢 Visa interviews are typically required for first-time applicants.\n• Schedule through your country's US embassy/consulate\n• Bring all required documents\n• Be prepared to explain your case\n• Dress professionally and arrive early\n• Answer questions honestly and directly"
    
    elif any(word in question for word in ["document", "paperwork", "required"]):
        response = "📋 Required documents vary by visa type but commonly include:\n• Valid passport\n• Application forms\n• Photos\n• Financial documents\n• Supporting evidence (job offer, school acceptance, etc.)\n• Medical exam (for some visas)\n• Police certificates\n\nSpecific requirements depend on your case type."
    
    else:
        response = "I can help with specific questions about:\n• Processing times and costs\n• Required documents\n• Interview preparation\n• Next steps for your case\n\nPlease ask a more specific question, or use the guided consultation for personalized advice."
    
    # Stream the response
    def stream_response():
        words = response.split()
        for word in words:
            yield f"data: {word} \n\n"
            time.sleep(0.03)
        
        # Log the Q&A
        try:
            log_conversation(req.question, response)
        except Exception as e:
            print(f"Error logging: {e}")
    
    return StreamingResponse(stream_response(), media_type="text/event-stream")

@app.post("/lead")
async def submit_lead(req: LeadRequest):
    """Enhanced lead capture with more details"""
    try:
        # Create more detailed lead entry
        lead_info = f"Goal: {req.goal}, Country: {req.current_country}"
        if req.timeline:
            lead_info += f", Timeline: {req.timeline}"
        if req.additional_info:
            lead_info += f", Notes: {req.additional_info}"
        
        create_lead(req.email, req.current_country, lead_info)
        return {"status": "success", "message": "Your information has been saved. We'll contact you within 24 hours."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": "guided_consultation",
        "database": "connected",
        "visa_types": len(VISA_TYPES)
    } 
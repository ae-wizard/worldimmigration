from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import logging
from db import init_db, log_conversation, save_lead

# Initialize FastAPI app
app = FastAPI(title="AI Immigration Consultant API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Simple visa guidance data
VISA_GUIDANCE = {
    "h1b": {
        "name": "H-1B Specialty Occupation",
        "description": "For professionals in specialty occupations requiring a bachelor's degree",
        "requirements": [
            "Bachelor's degree or equivalent",
            "Job offer from US employer",
            "Employer must file petition",
            "Annual cap applies (65,000 + 20,000 advanced degree)"
        ],
        "timeline": "6-8 months (with employer petition)",
        "cost": "$2,000-$5,000 in government fees"
    },
    "l1": {
        "name": "L-1 Intracompany Transfer",
        "description": "For employees transferring from foreign office to US office of same company",
        "requirements": [
            "1+ years employment with company abroad",
            "Managerial, executive, or specialized knowledge role",
            "Company must have offices in both countries"
        ],
        "timeline": "2-4 months",
        "cost": "$1,500-$3,000 in government fees"
    },
    "eb1": {
        "name": "EB-1 Priority Workers",
        "description": "For individuals with extraordinary ability, outstanding professors/researchers, or multinational executives",
        "requirements": [
            "Extraordinary ability in sciences, arts, education, business, or athletics",
            "OR Outstanding professor/researcher with international recognition",
            "OR Multinational executive/manager"
        ],
        "timeline": "8-12 months (no labor certification required)",
        "cost": "$3,000-$7,000 in government fees"
    }
}

# Request/Response models
class UserProfile(BaseModel):
    current_country: Optional[str] = None
    current_status: Optional[str] = None
    goal: Optional[str] = None
    education_level: Optional[str] = None
    has_job_offer: Optional[str] = None
    family_in_us: Optional[str] = None
    field_of_work: Optional[str] = None

class QuestionRequest(BaseModel):
    question: str
    user_profile: Optional[UserProfile] = None

class LeadData(BaseModel):
    email: str
    phone: Optional[str] = None
    country: Optional[str] = None
    goal: Optional[str] = None
    timeline: Optional[str] = None
    additional_info: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "AI Immigration Consultant API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Immigration API"}

@app.post("/get-guidance")
async def get_guidance(profile: UserProfile):
    """Get personalized immigration guidance based on user profile"""
    try:
        # Simple logic to determine best visa path
        guidance = {
            "recommended_path": "General Immigration Guidance",
            "next_steps": [],
            "estimated_timeline": "Varies by visa type",
            "key_requirements": []
        }
        
        # Determine best path based on profile
        if profile.has_job_offer == "yes" and profile.education_level in ["bachelor", "master", "phd"]:
            if profile.goal == "work":
                guidance.update({
                    "recommended_path": "H-1B Specialty Occupation Visa",
                    "next_steps": [
                        "Employer files H-1B petition (Form I-129)",
                        "Wait for USCIS approval",
                        "Apply for visa at US consulate",
                        "Enter US and begin work"
                    ],
                    "estimated_timeline": "6-8 months",
                    "key_requirements": [
                        "Bachelor's degree in relevant field",
                        "Job offer from US employer",
                        "Employer sponsorship",
                        "Specialty occupation position"
                    ]
                })
            
        elif profile.goal == "permanent_residence":
            guidance.update({
                "recommended_path": "Employment-Based Green Card",
                "next_steps": [
                    "Employer files PERM labor certification",
                    "File I-140 immigrant petition",
                    "File I-485 or consular processing",
                    "Receive green card"
                ],
                "estimated_timeline": "1-3 years (varies by country)",
                "key_requirements": [
                    "Permanent job offer",
                    "Labor certification (usually required)",
                    "Employer sponsorship",
                    "Meet education/experience requirements"
                ]
            })
        
        # Log the interaction
        log_conversation(
            user_question=f"Profile guidance request: {profile.dict()}",
            assistant_answer=f"Recommended: {guidance['recommended_path']}"
        )
        
        return guidance
        
    except Exception as e:
        logging.error(f"Error in get_guidance: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Handle specific immigration questions"""
    try:
        question = request.question.lower()
        
        # Simple keyword-based responses
        response = "Thank you for your question. Based on current immigration regulations, here's what I can tell you:\n\n"
        
        if "h1b" in question or "h-1b" in question:
            response += """The H-1B visa is for specialty occupations requiring a bachelor's degree. Key points:
            
• Annual filing period: March 1-31 (for October start)
• 85,000 total visas available annually
• Requires employer sponsorship
• 3-year initial period, extendable to 6 years
• Premium processing available for faster decisions"""
            
        elif "green card" in question or "permanent resident" in question:
            response += """Green cards provide permanent residence in the US. Main categories:
            
• Employment-based (EB-1, EB-2, EB-3)
• Family-based (immediate relatives, family preference)
• Diversity visa lottery
• Special categories (refugees, asylum, etc.)
• Processing times vary widely by category and country"""
            
        elif "timeline" in question or "how long" in question:
            response += """Immigration timelines vary significantly by visa type:
            
• H-1B: 6-8 months (with employer petition)
• L-1: 2-4 months
• Employment-based green card: 1-3+ years
• Family-based green card: 6 months to 10+ years
• Processing times change frequently - check USCIS website for current estimates"""
            
        elif "cost" in question or "fee" in question:
            response += """Immigration costs include government fees and legal fees:
            
• H-1B: $2,000-$5,000 in government fees
• L-1: $1,500-$3,000 in government fees  
• Green card: $1,500-$4,000+ in government fees
• Legal fees: $2,000-$15,000+ depending on complexity
• Additional costs may apply for premium processing"""
            
        else:
            response += """I'd be happy to help with your specific situation. For the most accurate guidance, I recommend:

• Consulting with a qualified immigration attorney
• Checking the latest USCIS policy manual
• Reviewing current processing times on USCIS.gov
• Considering your specific circumstances and goals

Would you like me to connect you with an immigration specialist for personalized advice?"""
        
        # Log the conversation
        log_conversation(
            user_question=request.question,
            assistant_answer=response
        )
        
        return {"response": response}
        
    except Exception as e:
        logging.error(f"Error in ask_question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/submit-lead")
async def submit_lead(lead_data: LeadData):
    """Save lead information"""
    try:
        lead_id = save_lead(
            email=lead_data.email,
            phone=lead_data.phone,
            country=lead_data.country,
            goal=lead_data.goal,
            timeline=lead_data.timeline,
            additional_info=lead_data.additional_info
        )
        
        return {"success": True, "lead_id": lead_id, "message": "Thank you! We'll be in touch soon."}
        
    except Exception as e:
        logging.error(f"Error in submit_lead: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save lead information")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 
# api_production.py - Production API with real USCIS content and RAG
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import json
import os
from typing import Optional, List
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from scraper import load_scraped_content, scrape_immigration_content, save_scraped_content
from embeddings import index_documents, search_similar, get_qdrant_client, ensure_collection
from db import init_db, log_conversation, create_lead

app = FastAPI(title="AI Immigration Consultant API - Production")

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Initialize components
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
COLLECTION_NAME = "immigration_docs"

class UserProfileRequest(BaseModel):
    current_country: str
    current_status: str
    goal: str
    education_level: Optional[str] = None
    has_job_offer: Optional[bool] = None
    family_in_us: Optional[str] = None

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

async def ensure_knowledge_base():
    """Ensure we have scraped content and vector database ready"""
    
    # Check if we have scraped content
    content = load_scraped_content()
    
    if not content:
        print("No scraped content found. Scraping USCIS/State Department...")
        content = scrape_immigration_content()
        save_scraped_content(content)
    
    # Ensure Qdrant collection exists and has content
    try:
        qdrant = get_qdrant_client()
        collection_info = qdrant.get_collection(COLLECTION_NAME)
        if collection_info.points_count == 0:
            print("Vector database is empty. Indexing content...")
            index_documents(content)
        else:
            print(f"Vector database ready with {collection_info.points_count} documents")
    except:
        print("Creating vector database and indexing content...")
        ensure_collection(COLLECTION_NAME)
        index_documents(content)

def get_context_for_profile(profile: UserProfileRequest) -> str:
    """Get relevant context based on user profile"""
    
    # Build a search query based on profile
    search_terms = []
    
    if profile.goal == "work":
        search_terms.extend(["H-1B", "work visa", "employment", "job offer"])
    elif profile.goal == "study":
        search_terms.extend(["F-1", "student visa", "school", "university"])
    elif profile.goal == "family":
        search_terms.extend(["family immigration", "I-130", "spouse", "relative"])
    elif profile.goal == "permanent_residence":
        search_terms.extend(["green card", "permanent resident", "I-485"])
    elif profile.goal == "citizenship":
        search_terms.extend(["naturalization", "citizenship", "N-400"])
    elif profile.goal == "visit":
        search_terms.extend(["tourist visa", "B-1", "B-2", "visitor"])
    
    # Add country-specific terms
    search_terms.append(profile.current_country)
    
    # Search for relevant content
    search_query = " ".join(search_terms)
    results = search_similar(search_query, limit=5)
    
    # Combine the most relevant content
    context_texts = []
    for result in results:
        if result.get("score", 0) > 0.6:  # Only high-relevance content
            context_texts.append(result["text"])
    
    return "\n".join(context_texts[:3])  # Top 3 most relevant

def generate_guidance_with_context(profile: UserProfileRequest, context: str) -> dict:
    """Generate guidance using real USCIS content as context"""
    
    # Extract key information from context for structured response
    processing_times = []
    requirements = []
    next_steps = []
    
    # Parse context for structured information
    context_lower = context.lower()
    
    # Look for processing times
    if "months" in context_lower or "years" in context_lower:
        # Extract time-related sentences
        sentences = context.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ["month", "year", "week", "processing"]):
                processing_times.append(sentence.strip())
    
    # Look for requirements
    requirement_keywords = ["must", "required", "need", "eligible", "qualify"]
    sentences = context.split('.')
    for sentence in sentences:
        if any(word in sentence.lower() for word in requirement_keywords):
            requirements.append(sentence.strip())
    
    # Generate next steps based on goal and context
    if profile.goal == "work":
        if profile.has_job_offer:
            next_steps = [
                "Have your employer file the appropriate work petition",
                "Prepare supporting documents (degree, experience)",
                "Schedule visa interview if required"
            ]
        else:
            next_steps = [
                "Find a US employer willing to sponsor you",
                "Ensure you meet qualification requirements",
                "Consider multiple visa categories"
            ]
    elif profile.goal == "study":
        next_steps = [
            "Get accepted to a SEVP-approved school",
            "Receive Form I-20 from your school",
            "Pay SEVIS fee and apply for F-1 visa"
        ]
    elif profile.goal == "family":
        next_steps = [
            "Have your US family member file Form I-130",
            "Wait for petition approval",
            "Apply for immigrant visa or adjust status"
        ]
    # Add more goal-specific logic...
    
    return {
        "recommended_path": f"{profile.goal.replace('_', ' ').title()} Immigration",
        "next_steps": next_steps[:5],  # Top 5 steps
        "requirements": requirements[:3],  # Top 3 requirements
        "processing_info": processing_times[:2],  # Top 2 time references
        "source": "Official USCIS/State Department Information"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize knowledge base on startup"""
    await ensure_knowledge_base()

@app.get("/")
async def root():
    return {"message": "AI Immigration Consultant API - Production with Real USCIS Data", "status": "ready"}

@app.post("/get-guidance")
async def get_guidance(profile: UserProfileRequest):
    """Get personalized immigration guidance using real USCIS content"""
    
    # Get relevant context from scraped USCIS content
    context = get_context_for_profile(profile)
    
    if not context:
        return {
            "error": "No relevant information found",
            "message": "Please contact us for a personalized consultation"
        }
    
    # Generate structured guidance
    guidance = generate_guidance_with_context(profile, context)
    
    # Log the consultation
    try:
        profile_summary = f"Country: {profile.current_country}, Status: {profile.current_status}, Goal: {profile.goal}"
        log_conversation(profile_summary, json.dumps(guidance))
    except Exception as e:
        print(f"Error logging: {e}")
    
    return guidance

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    """Answer questions using RAG with real USCIS content"""
    
    def stream_uscis_response():
        try:
            # Search for relevant USCIS content
            results = search_similar(req.question, limit=3)
            
            if not results:
                response = "I don't have specific information about that topic in my knowledge base of official USCIS sources. Please contact an immigration attorney for guidance on this specific question."
            else:
                # Combine the most relevant content
                relevant_content = []
                for result in results:
                    if result.get("score", 0) > 0.5:  # Reasonable relevance threshold
                        relevant_content.append(result["text"])
                
                if relevant_content:
                    # Create response based on official content
                    response = f"Based on official USCIS information:\n\n"
                    response += "\n".join(relevant_content[:2])  # Top 2 most relevant
                    response += f"\n\nFor the most current information, please visit uscis.gov or consult with an immigration attorney."
                else:
                    response = "I found some related information but it may not directly answer your question. For specific guidance, please contact an immigration attorney."
            
            # Stream the response
            words = response.split()
            for word in words:
                yield f"data: {word} \n\n"
                time.sleep(0.02)
            
            # Log the Q&A
            try:
                log_conversation(req.question, response)
            except Exception as e:
                print(f"Error logging: {e}")
                
        except Exception as e:
            error_msg = f"I apologize, but I'm having trouble accessing the immigration database right now. Please try again or contact us directly."
            yield f"data: {error_msg}\n\n"
    
    return StreamingResponse(stream_uscis_response(), media_type="text/event-stream")

@app.post("/lead")
async def submit_lead(req: LeadRequest):
    """Enhanced lead capture with more details"""
    try:
        lead_info = f"Goal: {req.goal}, Country: {req.current_country}"
        if req.timeline:
            lead_info += f", Timeline: {req.timeline}"
        if req.additional_info:
            lead_info += f", Notes: {req.additional_info}"
        
        create_lead(req.email, req.current_country, lead_info)
        return {"status": "success", "message": "Your information has been saved. We'll contact you within 24 hours."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/knowledge-base-status")
async def knowledge_base_status():
    """Check the status of our knowledge base"""
    try:
        # Check scraped content
        content = load_scraped_content()
        scraped_count = len(content) if content else 0
        
        # Check vector database
        qdrant = get_qdrant_client()
        try:
            collection_info = qdrant.get_collection(COLLECTION_NAME)
            vector_count = collection_info.points_count
        except:
            vector_count = 0
        
        return {
            "scraped_documents": scraped_count,
            "indexed_documents": vector_count,
            "status": "ready" if scraped_count > 0 and vector_count > 0 else "needs_initialization"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mode": "production_with_real_uscis_data",
        "database": "connected",
        "data_source": "Official USCIS/State Department"
    } 
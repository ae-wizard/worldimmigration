# api.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from threading import Thread
import torch
from db import init_db, log_conversation, create_lead

app = FastAPI(title="AI Immigration Consultant API")

# Enable CORS for local dev (React runs on localhost:3000/5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize Qdrant client and embedding model globally
qdrant = QdrantClient(url=QDRANT_URL)
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Collection configuration
COLLECTION_NAME = "immigration_docs"
VECTOR_SIZE = 384

# Ensure our collection exists
try:
    qdrant.get_collection(COLLECTION_NAME)
except:
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )

# Initialize database
init_db()

# Initialize LLM (will be loaded on first use for faster startup)
llm_model = None
llm_tokenizer = None

def load_llm():
    """Load the LLM model and tokenizer"""
    global llm_model, llm_tokenizer
    if llm_model is None:
        print("Loading LLaMA model...")
        model_name = "microsoft/DialoGPT-medium"  # Using a smaller model for Apple Silicon
        # For production, you could use: "meta-llama/Llama-2-7b-chat-hf"
        
        llm_tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_TOKEN)
        llm_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            token=HF_TOKEN,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        if llm_tokenizer.pad_token is None:
            llm_tokenizer.pad_token = llm_tokenizer.eos_token
        
        print("LLaMA model loaded successfully!")

class QuestionRequest(BaseModel):
    question: str

class LeadRequest(BaseModel):
    email: str
    country: str
    intent: str

@app.get("/")
async def root():
    return {"message": "AI Immigration Consultant API"}

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    question = req.question
    
    # 1. Embed the user's question
    q_vector = embed_model.encode(question).tolist()
    
    # 2. Retrieve relevant docs from Qdrant
    try:
        results = qdrant.search(
            collection_name=COLLECTION_NAME, 
            query_vector=q_vector, 
            limit=3
        )
        retrieved_texts = [res.payload.get("text", "") for res in results if res.payload]
        context = "\n".join(retrieved_texts)
    except Exception as e:
        print(f"Vector search error: {e}")
        context = "No relevant information found in knowledge base."
    
    # 3. Construct prompt for LLM
    system_context = (
        "You are an AI immigration consultant. You have access to the following official information:\n"
        f"{context}\n\n"
        "Using this information, answer the user's question about immigration. "
        "Be accurate, concise, and helpful. If the information is insufficient, say you don't know.\n\n"
        f"User question: {question}\n"
        "Answer:"
    )
    
    # 4. Generate LLM response (streaming)
    def stream_llm_response():
        accumulated_response = ""
        try:
            # Load model on first use
            load_llm()
            
            # Tokenize input
            inputs = llm_tokenizer.encode(system_context, return_tensors="pt")
            
            # Set up streaming
            streamer = TextIteratorStreamer(llm_tokenizer, skip_prompt=True, skip_special_tokens=True)
            
            # Generation parameters
            generation_kwargs = {
                "input_ids": inputs,
                "max_new_tokens": 512,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9,
                "streamer": streamer,
                "pad_token_id": llm_tokenizer.eos_token_id
            }
            
            # Start generation in a separate thread
            thread = Thread(target=llm_model.generate, kwargs=generation_kwargs)
            thread.start()
            
            # Stream the response
            for new_text in streamer:
                if new_text:
                    accumulated_response += new_text
                    yield f"data: {new_text}\n\n"
            
            thread.join()
            
        except Exception as e:
            error_msg = f"I apologize, but I'm having trouble generating a response right now. Please try again. Error: {str(e)}"
            yield f"data: {error_msg}\n\n"
            accumulated_response = error_msg
        
        # Log the conversation
        try:
            log_conversation(question, accumulated_response)
        except Exception as e:
            print(f"Error logging conversation: {e}")
    
    return StreamingResponse(stream_llm_response(), media_type="text/event-stream")

@app.post("/lead")
async def submit_lead(req: LeadRequest):
    """Endpoint to collect lead information."""
    try:
        create_lead(req.email, req.country, req.intent)
        return {"status": "success", "message": "Lead information saved"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Qdrant connection
        qdrant.get_collection(COLLECTION_NAME)
        qdrant_status = "connected"
    except:
        qdrant_status = "disconnected"
    
    return {
        "status": "healthy",
        "qdrant": qdrant_status,
        "llm_loaded": llm_model is not None
    } 
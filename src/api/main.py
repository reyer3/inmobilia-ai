"""FastAPI application for the Inmobilia AI web interface."""

from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config.settings import APP_NAME, APP_VERSION, DEBUG
from src.graphs.mvp_graph import build_mvp_graph


# Define models
class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str
    conversation_id: str
    is_lead_complete: bool
    extracted_data: Dict[str, Any]

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    debug=DEBUG,
    description="API for Inmobilia AI conversational agent"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for conversations (replace with DB in production)
conversations = {}

# Initialize the graph
mvp_graph = build_mvp_graph()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message and return response."""
    conversation_id = request.conversation_id
    
    # Create new conversation if no ID provided
    if not conversation_id or conversation_id not in conversations:
        conversation_id = f"conv_{len(conversations) + 1}"
        # Initialize state (will be done by welcome_handler)
        state = {}
    else:
        # Get existing state
        state = conversations[conversation_id]
    
    # Process message through graph
    try:
        new_state, response = mvp_graph.invoke(state, request.message)
        
        # Update conversation storage
        conversations[conversation_id] = new_state
        
        # Check if lead is complete
        is_lead_complete = is_core_lead_complete(new_state)
        
        # Extract data for response
        extracted_data = extract_lead_data(new_state)
        
        return ChatResponse(
            message=response,
            conversation_id=conversation_id,
            is_lead_complete=is_lead_complete,
            extracted_data=extracted_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def is_core_lead_complete(state):
    """Check if core lead data is complete."""
    if not state or not state.get("lead_data"):
        return False
        
    # Check mandatory fields
    lead_data = state["lead_data"]
    mandatory_fields = ["nombre", "tipo_inmueble", "consentimiento"]
    
    return all(lead_data.get(field) for field in mandatory_fields)

def extract_lead_data(state):
    """Extract lead data from state."""
    if not state or not state.get("lead_data"):
        return {}
        
    return state["lead_data"]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": APP_VERSION}

# Run with: uvicorn src.api.main:app --reload
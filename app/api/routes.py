import os
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EXPECTED_API_KEY = os.getenv("SUBMISSION_API_KEY")

router = APIRouter()

# -------------------------------------------------------------------
# Evaluator Request Models (MATCHES EXACT PAYLOAD THEY SEND)
# -------------------------------------------------------------------

class IncomingMessage(BaseModel):
    sender: str
    text: str
    timestamp: int

class EvaluatorRequest(BaseModel):
    sessionId: str
    message: IncomingMessage
    conversationHistory: list
    metadata: dict

# -------------------------------------------------------------------
# Evaluator Response Model (MATCHES EXACT EXPECTED RESPONSE)
# -------------------------------------------------------------------

class EvaluatorResponse(BaseModel):
    status: str
    reply: str

# -------------------------------------------------------------------
# Chat Endpoint (Evaluator-Compatible)
# -------------------------------------------------------------------

@router.post("/chat", response_model=EvaluatorResponse)
async def chat_endpoint(
    payload: EvaluatorRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    # ---------------- API KEY VALIDATION ----------------
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    user_text = payload.message.text.lower()

    # ---------------- SIMPLE SCAM LOGIC ----------------
    scam_keywords = [
        "bank",
        "account",
        "verify",
        "blocked",
        "urgent",
        "suspend",
        "suspended"
    ]

    if any(keyword in user_text for keyword in scam_keywords):
        reply_text = "Why is my account being suspended?"
    else:
        reply_text = "Who are you and why are you messaging me?"

    # ---------------- REQUIRED RESPONSE ----------------
    return {
        "status": "success",
        "reply": reply_text
    }

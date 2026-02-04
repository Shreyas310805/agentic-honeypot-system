import os
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

EXPECTED_API_KEY = os.getenv("SUBMISSION_API_KEY")

router = APIRouter()

# -------- Evaluator Request Models --------

class IncomingMessage(BaseModel):
    sender: str
    text: str
    timestamp: int

class EvaluatorRequest(BaseModel):
    sessionId: str
    message: IncomingMessage
    conversationHistory: list
    metadata: dict

# -------- Evaluator Response Model --------

class EvaluatorResponse(BaseModel):
    status: str
    reply: str

# -------- Chat Endpoint --------

@router.post("/chat", response_model=EvaluatorResponse)
async def chat_endpoint(
    payload: EvaluatorRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    text = payload.message.text.lower()

    scam_keywords = [
        "bank", "account", "verify",
        "blocked", "urgent", "suspend", "suspended"
    ]

    if any(word in text for word in scam_keywords):
        reply = "Why is my account being suspended?"
    else:
        reply = "Who are you and why are you messaging me?"

    return {
        "status": "success",
        "reply": reply
    }

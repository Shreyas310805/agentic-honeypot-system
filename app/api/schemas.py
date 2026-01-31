from pydantic import BaseModel, Field
from typing import List, Optional

# --- INPUT SCHEMAS (What the Scammer API sends you) ---

class Message(BaseModel):
    role: str       # "user" (scammer) or "assistant" (your agent)
    content: str    # The actual text message

class ChatRequest(BaseModel):
    session_id: str
    messages: List[Message]  # History of the conversation

# --- OUTPUT SCHEMAS (What you send back) ---

class Intelligence(BaseModel):
    bank_accounts: List[str] = []
    upi_ids: List[str] = []
    phishing_links: List[str] = []

class EngagementMetrics(BaseModel):
    turn_count: int = 0
    duration_seconds: int = 0

class ChatResponse(BaseModel):
    scam_detection_status: str  # e.g., "detected", "suspected", "safe"
    reply: str                  # What your Agent says back to the scammer
    extracted_intelligence: Intelligence
    engagement_metrics: EngagementMetrics
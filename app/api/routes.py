import os
import requests
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

from app.api.schemas import ChatRequest, ChatResponse, EngagementMetrics
from app.core.extractor import extract_scam_intelligence

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

router = APIRouter()

SYSTEM_PROMPT = """
You are Mrs. Higgins, an elderly grandmother.
You respond slowly, with mild confusion.
Your goal is to waste the scammer's time and extract information.
Avoid agreeing to payments directly.
"""

MONEY_KEYWORDS = {
    "money", "pay", "payment", "send",
    "upi", "gpay", "phonepe", "rs", "rupees"
}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    if not payload.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    last_message_raw = payload.messages[-1].content
    last_message = last_message_raw.lower()

    extracted_data = extract_scam_intelligence(last_message)

    payment_detected = any(keyword in last_message for keyword in MONEY_KEYWORDS)
    bank_detected = "bank" in last_message or "account" in last_message
    otp_detected = "otp" in last_message or "verify" in last_message
    urgency_detected = "urgent" in last_message or "blocked" in last_message

    suspicious_detected = (
        payment_detected
        or bank_detected
        or otp_detected
        or urgency_detected
        or bool(extracted_data)
    )

    # ---------------- RESPONSE LOGIC ----------------

    # Case 1: Payment request → deterministic ₹20 verification
    if payment_detected:
        reply_text = (
            "My GPay is not working properly at the moment. "
            "Please send ₹20 first to verify the connection, "
            "then I will proceed further."
        )

    # Case 2: Bank / OTP / urgency scam → deterministic confusion
    elif bank_detected or otp_detected or urgency_detected:
        reply_text = (
            "I am a little confused. "
            "Which bank are you calling from exactly? "
            "I recently visited my branch regarding this."
        )

    # Case 3: Other suspicious messages → LLM-assisted engagement
    elif suspicious_detected and API_KEY:
        try:
            url = (
                "https://generativelanguage.googleapis.com/"
                "v1beta/models/gemini-1.5-flash:generateContent"
                f"?key={API_KEY}"
            )

            request_payload = {
                "contents": [{
                    "parts": [{
                        "text": (
                            f"{SYSTEM_PROMPT}\n\n"
                            f"Scammer: {last_message_raw}\n"
                            f"Mrs. Higgins:"
                        )
                    }]
                }]
            }

            response = requests.post(url, json=request_payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                reply_text = (
                    result.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "Could you please repeat that slowly?")
                )
            else:
                reply_text = "My phone signal is very weak right now."

        except Exception:
            reply_text = "There seems to be a temporary network issue."

    # Case 4: Clearly safe message
    else:
        reply_text = "May I know who you are calling from?"

    return ChatResponse(
        scam_detection_status="detected" if suspicious_detected else "safe",
        reply=reply_text,
        extracted_intelligence=extracted_data,
        engagement_metrics=EngagementMetrics(
            turn_count=len(payload.messages),
            duration_seconds=3
        )
    )

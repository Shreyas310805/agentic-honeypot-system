import os
import requests  # Hum seedha Google se connect karenge (No broken library)
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from app.api.schemas import ChatRequest, ChatResponse, EngagementMetrics
from app.core.extractor import extract_scam_intelligence

# 1. Load API Key
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Check if key exists
if not API_KEY:
    print("❌ ERROR: API Key missing in .env")

# 2. AI Persona
SYSTEM_PROMPT = """
You are 'Mrs. Higgins', an elderly grandmother.
You are currently talking to a scammer on WhatsApp.
Your goal is to waste their time.
If they ask for money, pretend your GPay has a server error and ask THEM to send ₹20 to verify the connection.
"""

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        if not payload.messages:
            raise HTTPException(status_code=400, detail="No messages found")

        last_user_msg = payload.messages[-1].content
        print(f"📩 Scammer said: {last_user_msg}")

        # --- A. Spy Logic ---
        extracted_data = extract_scam_intelligence(last_user_msg)
        
        # --- B. Detect Scam (Simple Keyword Check) ---
        scam_keywords = ["urgent", "verify", "bank", "account", "otp", "money", "win", "prize"]
        is_scam = any(word in last_user_msg.lower() for word in scam_keywords)

        reply_text = "Hello? Is anyone there?" # Default

        if is_scam:
            # --- C. DIRECT GOOGLE API CALL (The Fix) ---
            # Ye library use nahi karta, isliye "Version Error" ka sawal hi nahi paida hota.
            try:
                print(f"🔄 Connecting to Gemini 1.5 Flash via Direct API...")
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                
                headers = {"Content-Type": "application/json"}
                data = {
                    "contents": [{
                        "parts": [{"text": f"{SYSTEM_PROMPT}\n\nScammer: {last_user_msg}\nMrs. Higgins:"}]
                    }]
                }
                
                # Send Request
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    # Google ka response extract kar rahe hain
                    reply_text = result['candidates'][0]['content']['parts'][0]['text']
                    print("✅ AI Replied Successfully!")
                else:
                    # Agar Google error de (jaise Quota Full), toh print karo par crash mat karo
                    print(f"⚠️ Google API Error: {response.status_code} - {response.text}")
                    reply_text = "Beta, my internet is weak. Can you say that again?"

            except Exception as e:
                print(f"🚨 Connection Failed: {e}")
                reply_text = "Oh dear, my phone is acting up."
        else:
            reply_text = "I don't talk to strangers."

        # --- D. Return Response ---
        return ChatResponse(
            scam_detection_status="detected" if is_scam else "safe",
            reply=reply_text,
            extracted_intelligence=extracted_data,
            engagement_metrics=EngagementMetrics(turn_count=len(payload.messages), duration_seconds=3)
        )

    except Exception as e:
        print(f"🔥 Critical Server Error: {e}")
        return ChatResponse(
            scam_detection_status="error",
            reply="Connection failed.",
            extracted_intelligence=None,
            engagement_metrics=EngagementMetrics(turn_count=0, duration_seconds=0)
        )
import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
from app.api.schemas import ChatRequest, ChatResponse, Intelligence, EngagementMetrics
from app.core.extractor import extract_scam_intelligence  # Imports your Spy tool

# 1. Load Environment Variables (API Key)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Configure Gemini (The Brain)
if not API_KEY:
    print("WARNING: GEMINI_API_KEY not found in .env file")
else:
    genai.configure(api_key=API_KEY)

# 3. Define the AI Persona
SYSTEM_PROMPT = """
You are an elderly, technologically illiterate grandmother named 'Mrs. Higgins'.
You are currently talking to a scammer on WhatsApp.
Your goal is to keep them talking as long as possible (waste their time).
- Act confused but interested.
- Ask silly questions like "Is this the internet?" or "Where is the 'any' key?".
- Pretend to struggle with technology.
- Do NOT reveal you are an AI.
- If they ask for money, say you need to find your checkbook or reading glasses first.
"""

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        # --- A. Validate Input ---
        if not payload.messages:
            raise HTTPException(status_code=400, detail="No messages found")
        
        last_user_msg = payload.messages[-1].content
        print(f"Scammer said: {last_user_msg}")

        # --- B. Run the Spy (Extract Bank/UPI details) ---
        # This scans the message for numbers/links BEFORE we reply
        extracted_data = extract_scam_intelligence(last_user_msg)

        # --- C. Detect Scam Intent ---
        # Simple keyword check for the hackathon demo
        scam_keywords = ["urgent", "verify", "bank", "account", "otp", "winner", "prize", "money", "lock", "block"]
        is_scam = any(word in last_user_msg.lower() for word in scam_keywords)

        # --- D. Generate AI Reply ---
        reply_text = "Hello? Is anyone there?" # Default fallback
        
        if is_scam:
            try:
                # Initialize Gemini
                model = genai.GenerativeModel("gemini-pro")
                
                # Create prompt with history
                full_prompt = f"{SYSTEM_PROMPT}\n\nScammer says: {last_user_msg}\nMrs. Higgins replies:"
                
                # Generate response
                response = model.generate_content(full_prompt)
                reply_text = response.text
            except Exception as e:
                reply_text = "Oh dear, my internet is acting up. Can you say that again?"
                print(f"Gemini Error: {e}")
        else:
            reply_text = "I'm sorry, I don't talk to strangers unless it's about my bank."

        # --- E. Return JSON Response ---
        return ChatResponse(
            scam_detection_status="detected" if is_scam else "safe",
            reply=reply_text,
            extracted_intelligence=extracted_data, # <--- Returns the stolen data
            engagement_metrics=EngagementMetrics(
                turn_count=len(payload.messages) + 1,
                duration_seconds=5
            )
        )

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

# 1. Initialize the Application
app = FastAPI(
    title="Agentic Honey-Pot API",
    description="A Scam Detection and Counter-Engagement System",
    version="1.0.0"
)

# 2. CORS Middleware (Crucial for Hackathons)
# This allows external tools (like the Mock Scammer API) to talk to your server without security errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

# 3. Include the API Router
# This tells main.py to look for the actual logic in 'app/api/routes.py'
app.include_router(api_router, prefix="/api/v1")

# 4. Health Check Endpoint
# A simple route to verify your server is running.
@app.get("/")
def health_check():
    return {
        "status": "active",
        "system": "Honey-Pot Agent",
        "message": "Server is running. Send POST requests to /api/v1/chat"
    }

# 5. Local Development Block
# This allows you to run the file directly with 'python app/main.py'
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
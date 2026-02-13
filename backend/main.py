from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import routes
from backend.config import DEBUG

app = FastAPI(title="CMYK Splitter API")

# Log debug mode status on startup
@app.on_event("startup")
async def startup_event():
    if DEBUG:
        print("=" * 50)
        print("DEBUG MODE ENABLED")
        print("Verbose logging and debug file output active")
        print("=" * 50)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

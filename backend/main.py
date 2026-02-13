from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import routes

app = FastAPI(title="CMYK Splitter API")

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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .routes import search, upload, health


app = FastAPI(
    title="AI Powered Cloud Search Engine",
    description="Semantic Search + RAG powered by AWS + OpenAI",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])


@app.get("/")
def root():
    return {
        "message": "AI Cloud Search Engine is Running",
        "status": "ok"
    }
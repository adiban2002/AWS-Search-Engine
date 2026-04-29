from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # ১. এটা ইম্পোর্ট কর
from backend.app.config import Config
from backend.app.routes import search, upload, health


Config.validate_config()

app = FastAPI(
    title=Config.APP_NAME,
    version=Config.VERSION
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(search.router, prefix="/api/search")
app.include_router(upload.router, prefix="/api/upload")
app.include_router(health.router, prefix="/api/health")

@app.get("/")
def root():
    return {"message": f"Welcome to {Config.APP_NAME}"}
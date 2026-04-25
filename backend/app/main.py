from fastapi import FastAPI
from backend.app.config import Config
from backend.app.routes import search, upload, health


Config.validate_config()

app = FastAPI(
    title=Config.APP_NAME,
    version=Config.VERSION
)


app.include_router(search.router, prefix="/api/search")
app.include_router(upload.router, prefix="/api/upload")
app.include_router(health.router, prefix="/api/health")

@app.get("/")
def root():
    return {"message": f"Welcome to {Config.APP_NAME}"}
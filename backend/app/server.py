import uvicorn
import os

def start():
    uvicorn.run(
        "backend.app.main:app", 
        host="0.0.0.0", 
        port=8002, 
        reload=True  
    )

if __name__ == "__main__":
    start()
from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/")
def upload_file(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "message": "File uploaded successfully"
    }
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()



class SearchRequest(BaseModel):
    query: str



class SearchResponse(BaseModel):
    query: str
    results: list


@router.post("/", response_model=SearchResponse)
def search(request: SearchRequest):
    return {
        "query": request.query,
        "results": []
    }
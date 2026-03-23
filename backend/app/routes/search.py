from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.search_service import SearchService

router = APIRouter()


class SearchRequest(BaseModel):
    query: str


@router.post("/")
def search(request: SearchRequest):
    return SearchService.search(request.query)
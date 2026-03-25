from pydantic import BaseModel
from typing import Optional, List


class Document(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: Optional[dict] = None


class SearchQuery(BaseModel):
    query: str


class SearchResult(BaseModel):
    text: str
    score: Optional[float] = None
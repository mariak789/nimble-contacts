from fastapi import FastAPI, Query
from pydantic import BaseModel, conint
from .search import search_contacts

app = FastAPI(title="Nimble Contacts Search")

class Contact(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    description: str | None = None
    rank: float | None = None

@app.get("/search", response_model=list[Contact])
def search(
    q: str = Query(..., min_length=1, description="Full-text query"),
    limit: conint(ge=1, le=100) = 20,
    offset: conint(ge=0) = 0,
):
    rows = search_contacts(q=q, limit=limit, offset=offset)
    return rows

@app.get("/health")
def health():
    return {"ok": True}
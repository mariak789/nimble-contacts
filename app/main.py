from fastapi import FastAPI, Query
from .search import search_contacts

app = FastAPI(title="Contacts Search")

@app.get("/search")
def search(q: str = Query(..., min_length=1, max_length=128)):
    return search_contacts(q)
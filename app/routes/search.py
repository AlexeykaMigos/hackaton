from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services.search_service import search_stes
from app.templates.search_template import render_search_page

router = APIRouter()

@router.get("/search", response_class=HTMLResponse)
def search_route(q: str = ""):
    results = search_stes(q)
    return render_search_page(q, results)

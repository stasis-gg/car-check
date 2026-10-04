from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.api.aggregator import aggregator
import os
from typing import Optional

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/", response_class=HTMLResponse)
async def serve_home(request: Request, q: str = Query(None)):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_query": q or ""}
    )

@router.get("/report/{query}", response_class=HTMLResponse)
async def serve_report(request: Request, query: str):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"initial_query": query}
    )

@router.get("/api/check")
async def api_check_car(
    query: Optional[str] = Query(None),
    plate: Optional[str] = Query(None),
    vin: Optional[str] = Query(None)
):
    raw_query = query or f"{plate or ''} {vin or ''}".strip()
    data = await aggregator.check_all(raw_input=raw_query, plate=plate, vin=vin)
    return JSONResponse(content=data)

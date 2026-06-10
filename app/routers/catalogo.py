from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.db import get_productos, get_tc
import os, hashlib
from datetime import datetime

router    = APIRouter()
templates = Jinja2Templates(directory="app/templates")
WA_NUMBER = os.getenv("WHATSAPP_NUMBER","59170178698")

SECRET    = os.getenv("SECRET_KEY","titanium_secret_key_32_chars_min!")
MAYOR_TOKEN = hashlib.sha256((SECRET + "_mayor").encode()).hexdigest()[:12]

def serializar_productos(productos):
    """Convierte datetime a string para JSON"""
    if not productos:
        return []
    
    productos_serializados = []
    for p in productos:
        if isinstance(p, dict):
            p_dict = p.copy()
        else:
            p_dict = dict(p)
        
        for key, value in p_dict.items():
            if isinstance(value, datetime):
                p_dict[key] = value.isoformat()
        productos_serializados.append(p_dict)
    return productos_serializados

@router.get("/catalogo", response_class=HTMLResponse)
async def minorista(request: Request):
    db = request.app.state.db
    productos = await get_productos(db)
    productos = serializar_productos(productos)
    tc = await get_tc(db)
    
    return templates.TemplateResponse(request, "pages/minorista.html", {
        "productos": productos, 
        "tc": tc, 
        "wa_number": WA_NUMBER
    })

@router.get("/mayor/{token}", response_class=HTMLResponse)
async def mayorista(request: Request, token: str):
    if token != MAYOR_TOKEN:
        from fastapi.responses import HTMLResponse
        return HTMLResponse("<h2>Página no encontrada</h2>", status_code=404)
    
    db = request.app.state.db
    productos = await get_productos(db)
    productos = serializar_productos(productos)
    tc = await get_tc(db)
    
    return templates.TemplateResponse(request, "pages/mayorista.html", {
        "productos": productos, 
        "tc": tc, 
        "wa_number": WA_NUMBER
    })

@router.get("/mayor-url")
async def get_mayor_url(request: Request):
    from app.auth import require_admin
    require_admin(request)
    host = str(request.base_url).rstrip("/")
    return {"url": f"{host}/mayor/{MAYOR_TOKEN}"}
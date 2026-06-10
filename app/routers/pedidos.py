from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/pedido/{pedido_id}", response_class=HTMLResponse)
async def ver_pedido(request: Request, pedido_id: int):
    return templates.TemplateResponse("pages/pedido_confirmacion.html", {
        "request": request,
        "pedido_id": pedido_id
    })

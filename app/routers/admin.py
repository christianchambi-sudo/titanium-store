from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth import authenticate, create_token, require_admin, get_current_user

router    = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if get_current_user(request):
        return RedirectResponse("/tienda/admin/panel", 302)
    return templates.TemplateResponse(request, "pages/admin_login.html", {})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request,
                     username: str = Form(...),
                     password: str = Form(...)):
    user = authenticate(username, password)
    if not user:
        return templates.TemplateResponse(request, "pages/admin_login.html",
            {"error": "Usuario o contraseña incorrectos"})
    token = create_token(user)
    resp  = RedirectResponse("/tienda/admin/panel", status_code=302)  # ← CAMBIADO
    resp.set_cookie("ts_auth", token, httponly=True, max_age=3600*8, samesite="lax")
    return resp

@router.get("/panel", response_class=HTMLResponse)
async def panel(request: Request):
    user = require_admin(request)
    db   = request.app.state.db
    return templates.TemplateResponse(request, "pages/admin_panel.html",
        {"user": user, "db_ok": db is not None})

@router.get("/salir")
async def salir():
    resp = RedirectResponse("/tienda/admin/login", 302)  # También cambia esta
    resp.delete_cookie("ts_auth")
    return resp

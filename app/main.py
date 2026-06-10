from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncpg, os
from dotenv import load_dotenv
from app.routers import catalogo, admin, api, productos

load_dotenv()
templates = Jinja2Templates(directory="app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.db = await asyncpg.create_pool(
            os.getenv("DATABASE_URL","postgresql://postgres:postgres@localhost:5432/titanium_store"),
            min_size=2, max_size=10)
        print("✅ PostgreSQL conectado")
    except Exception as e:
        print(f"⚠️  Sin BD ({e}) — modo demo activo")
        app.state.db = None
    yield
    if app.state.db:
        await app.state.db.close()

app = FastAPI(title="Titanium Store", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.state.templates = templates

app.include_router(catalogo.router)
app.include_router(admin.router)
app.include_router(api.router)
app.include_router(productos.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    from app.db import get_productos, get_tc
    db = request.app.state.db
    return templates.TemplateResponse(request, "pages/minorista.html",
        {"productos": await get_productos(db), "tc": await get_tc(db),
         "wa_number": os.getenv("WHATSAPP_NUMBER","59170000000")})

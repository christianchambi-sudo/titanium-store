
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncpg, os
from dotenv import load_dotenv
from app.routers import catalogo, admin, api, productos

# Configurar logging para que se vea en journalctl
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()
templates = Jinja2Templates(directory="app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conectar a la base de datos
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/titanium_store")
    logger.info(f"Intentando conectar a BD con URL: {db_url[:50]}...")
    try:
        app.state.db = await asyncpg.create_pool(
            db_url,
            min_size=2,
            max_size=10
        )
        logger.info("✅ PostgreSQL conectado exitosamente")
    except Exception as e:
        logger.error(f"❌ Error conectando a PostgreSQL: {e}")
        app.state.db = None
    
    yield
    
    # Cerrar conexión al apagar
    if hasattr(app.state, 'db') and app.state.db:
        await app.state.db.close()
        logger.info("🔌 Conexión a BD cerrada")

# Crear la aplicación FastAPI
app = FastAPI(
    title="TITANIUM STORE",
    version="1.0",
    root_path="/tienda",
    lifespan=lifespan,
    max_request_size=20 * 1024 * 1024  # 20MB
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Incluir routers
app.include_router(catalogo.router)
app.include_router(admin.router)
app.include_router(api.router)
app.include_router(productos.router)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("pages/minorista.html", {"request": request})

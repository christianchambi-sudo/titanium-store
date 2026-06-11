print("=== API.PY CARGADO ===", flush=True)
from fastapi import APIRouter, Request, HTTPException
from app.db import get_productos, get_tc, DEMO_TC
from app.auth import get_current_user, require_admin
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter(prefix="/api")

# ── TC ──────────────────────────────────────────────────────
@router.get("/tc")
async def api_tc(request: Request):
    tc = await get_tc(request.app.state.db)
    return {"tc": tc}

class TCUpdate(BaseModel):
    valor: float

@router.post("/tc")
async def update_tc(data: TCUpdate, request: Request):
    require_admin(request)
    db = request.app.state.db
    if db:
        async with db.acquire() as c:
            await c.execute("UPDATE tipo_cambio SET activo=FALSE WHERE activo=TRUE")
            await c.execute("INSERT INTO tipo_cambio(valor,fuente,activo) VALUES($1,'manual',TRUE)", data.valor)
    return {"ok": True, "tc": data.valor}

# ── Productos ────────────────────────────────────────────────
# ── Productos ────────────────────────────────────────────────
# ── Productos ────────────────────────────────────────────────
@router.get("/productos")
async def api_productos(request: Request, incluir_inactivos: bool = False):
    import sys
    print("=== DEBUG: NUEVA FUNCIÓN api_productos EJECUTÁNDOSE ===", file=sys.stderr, flush=True)
    from app.db import get_tc
    import asyncpg
    import os
    from dotenv import load_dotenv
    from app.auth import get_current_user
    
    db = request.app.state.db
    tc = await get_tc(db)
    user = get_current_user(request)
    
    print(f"DEBUG: tc = {tc}", flush=True)
    print(f"DEBUG: user = {user}", flush=True)
    
    # Si no es admin, forzar incluir_inactivos=False
    if not user:
        incluir_inactivos = False
    
    print(f"DEBUG: incluir_inactivos = {incluir_inactivos}", flush=True)
    
    # Cargar variables de entorno
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    print(f"DEBUG: db_url = {db_url[:30]}..." if db_url else "DEBUG: db_url es None", flush=True)
    
    try:
        # Conectar directamente a PostgreSQL
        print("DEBUG: Intentando conectar a PostgreSQL...", flush=True)
        conn = await asyncpg.connect(db_url)
        print("DEBUG: Conexión exitosa!", flush=True)
        
        # Construir la consulta
        where_clause = "" if incluir_inactivos else "WHERE p.activo = TRUE"
        print(f"DEBUG: where_clause = {where_clause}", flush=True)
        
        query = """
            SELECT p.*, m.nombre as marca, c.nombre as categoria,
            ROUND(p.precio_venta_mayor_usd * $1, 2) as precio_mayor_bob,
            ROUND(p.precio_venta_mayor_usd * $1 + p.recargo_bob, 2) as precio_minorista_bob,
            $1 as tc_activo,
            COALESCE(
                (SELECT json_agg(json_build_object('id',i.id,'url',i.url,'orden',i.orden,'es_portada',i.es_portada)
                 ORDER BY i.orden)
                 FROM imagenes_producto i WHERE i.producto_id = p.id), '[]'::json
            ) as imagenes
            FROM productos p
            JOIN marcas m ON m.id = p.marca_id
            JOIN categorias c ON c.id = p.categoria_id
        """
        
        if not incluir_inactivos:
            query += " WHERE p.activo = TRUE"
        
        query += " ORDER BY p.orden, p.id"        
        print("DEBUG: Ejecutando consulta SQL...", flush=True)
        rows = await conn.fetch(query, tc)
        print(f"DEBUG: Consulta ejecutada, {len(rows)} filas obtenidas", flush=True)
        
        await conn.close()
        print("DEBUG: Conexión cerrada", flush=True)
        
        # Convertir filas a diccionarios
        productos = []
        for idx, row in enumerate(rows):
            prod = dict(row)
            print(f"DEBUG: Procesando fila {idx}, keys: {list(prod.keys())[:5]}...", flush=True)
            
            # Asegurar que 'imagenes' sea una lista válida
            if isinstance(prod.get('imagenes'), str):
                import json as json_lib
                try:
                    prod['imagenes'] = json_lib.loads(prod['imagenes'])
                    print(f"DEBUG: imagenes parseadas, {len(prod['imagenes'])} imágenes", flush=True)
                except:
                    prod['imagenes'] = []
            elif prod.get('imagenes') is None:
                prod['imagenes'] = []
            
            # Si no es admin, eliminar datos sensibles
            if not user:
                prod.pop("precio_venta_mayor_usd", None)
                prod.pop("recargo_bob", None)
                prod.pop("cajas_en_stock", None)
                prod.pop("unidades_por_caja", None)
            
            productos.append(prod)
        
        print(f"DEBUG: Procesamiento completado, {len(productos)} productos", flush=True)
        return productos
        
    except Exception as e:
        import traceback
        print(f"ERROR en api_productos: {e}", flush=True)
        print(f"TRACEBACK: {traceback.format_exc()}", flush=True)
        # Fallback: usar get_productos original
        prods = await get_productos(db)
        if not user:
            for p in prods:
                p.pop("precio_venta_mayor_usd", None)
                p.pop("recargo_bob", None)
                p.pop("cajas_en_stock", None)
                p.pop("unidades_por_caja", None)
        return prods

# ── Pedidos ──────────────────────────────────────────────────
class ItemPedido(BaseModel):
    producto_id: int
    codigo: str
    cantidad: int
    precio_bob: float
    precio_usd: float
    subtotal_bob: float
    subtotal_usd: float
    es_pedido_previo: bool = False

class PedidoCreate(BaseModel):
    tipo: str
    cliente_nombre: Optional[str] = None
    cliente_whatsapp: Optional[str] = None
    tc_usado: float
    items: list[ItemPedido]
    total_bob: float
    total_usd: float

@router.post("/pedidos")
async def crear_pedido(data: PedidoCreate, request: Request):
    db = request.app.state.db
    pid = None
    if db:
        try:
            async with db.acquire() as c:
                pid = await c.fetchval(
                    """INSERT INTO pedidos(tipo,tc_usado,subtotal_bob,subtotal_usd,total_bob,total_usd,canal,estado)
                       VALUES($1,$2,$3,$4,$5,$6,'whatsapp','pendiente') RETURNING id""",
                    data.tipo, data.tc_usado, data.total_bob, data.total_usd, data.total_bob, data.total_usd)
                for it in data.items:
                    await c.execute(
                        """INSERT INTO pedido_detalle(pedido_id,producto_id,cantidad,precio_orig_bob,precio_orig_usd,
                           precio_rebajado_bob,precio_rebajado_usd,subtotal_bob,subtotal_usd)
                           VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9)""",
                        pid, it.producto_id, it.cantidad,
                        it.precio_bob, it.precio_usd,
                        it.precio_bob, it.precio_usd,
                        it.subtotal_bob, it.subtotal_usd)
        except Exception as e:
            print(f"Error pedido: {e}")
    return {"ok": True, "pedido_id": pid or 0}

@router.get("/pedidos")
async def listar_pedidos(request: Request):
    require_admin(request)
    db = request.app.state.db
    if not db: return []
    rows = await db.fetch("SELECT * FROM v_pedidos_resumen LIMIT 100")
    return [dict(r) for r in rows]

@router.post("/pedidos/{pid}/confirmar")
async def confirmar_pedido(pid: int, request: Request):
    require_admin(request)
    db = request.app.state.db
    if db:
        await db.execute("UPDATE pedidos SET estado='confirmado',confirmado_en=NOW() WHERE id=$1", pid)
    return {"ok": True}

# ── Clientes ─────────────────────────────────────────────────
@router.get("/clientes")
async def listar_clientes(request: Request):
    require_admin(request)
    db = request.app.state.db
    if not db: return []
    rows = await db.fetch("SELECT * FROM clientes WHERE activo=TRUE ORDER BY nombre")
    return [dict(r) for r in rows]

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
@router.get("/productos")
async def api_productos(request: Request):
    prods = await get_productos(request.app.state.db)
    user = get_current_user(request)
    if not user:
        for p in prods:
            p.pop("precio_venta_mayor_usd", None)
            p.pop("recargo_bob", None)
            p.pop("cajas_en_stock", None)
            p.pop("unidades_por_caja", None)
    return prods

class ProductoUpdate(BaseModel):
    precio_venta_mayor_usd: Optional[float] = None
    recargo_bob: Optional[float] = None
    stock_fisico: Optional[bool] = None
    activo: Optional[bool] = None
    cajas_en_stock: Optional[int] = None
    unidades_por_caja: Optional[int] = None

@router.patch("/productos/{pid}")
async def update_producto(pid: int, data: ProductoUpdate, request: Request):
    require_admin(request)
    db = request.app.state.db
    if not db: return {"ok": True, "demo": True}
    fields = {k: v for k, v in data.dict().items() if v is not None}
    if not fields: return {"ok": True}
    sets = ", ".join(f"{k}=${i+2}" for i, k in enumerate(fields))
    vals = list(fields.values())
    await db.execute(f"UPDATE productos SET {sets}, actualizado_en=NOW() WHERE id=$1", pid, *vals)
    return {"ok": True}

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

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, List
import os, shutil, uuid, json
from app.utils.imagenes import optimizar_y_guardar_imagen, eliminar_imagen

router = APIRouter(prefix="/api/productos")
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def require_admin(request: Request):
    from app.auth import require_admin as _ra
    return _ra(request)

# ── Listar ───────────────────────────────────────────────────
@router.get("")
async def listar(request: Request, incluir_inactivos: bool = False):
    from app.db import get_tc, DEMO_PRODUCTOS, calcular_precios
    require_admin(request)
    db = request.app.state.db
    tc = await get_tc(db)
    if db:
        try:
            query = """
                SELECT p.*, m.nombre as marca, c.nombre as categoria_nombre,
                ROUND(p.precio_venta_mayor_usd * tc.valor, 2) as precio_mayor_bob,
                ROUND(p.precio_venta_mayor_usd * tc.valor + p.recargo_bob, 2) as precio_minorista_bob,
                tc.valor as tc_activo,
                COALESCE(
                    (SELECT json_agg(json_build_object('id',i.id,'url',i.url,'orden',i.orden,'es_portada',i.es_portada)
                     ORDER BY i.orden)
                     FROM imagenes_producto i WHERE i.producto_id = p.id), '[]'
                ) as imagenes
                FROM productos p
                JOIN marcas m ON m.id = p.marca_id
                JOIN categorias c ON c.id = p.categoria_id
                CROSS JOIN (SELECT valor FROM tipo_cambio WHERE activo=TRUE LIMIT 1) tc
                {}
                ORDER BY p.orden, p.id
            """.format("" if incluir_inactivos else "WHERE p.activo = TRUE")
            rows = await db.fetch(query)
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB error: {e}")
    # Demo
    return [calcular_precios(dict(p), tc) for p in DEMO_PRODUCTOS]

# ── Crear ────────────────────────────────────────────────────
@router.post("")
async def crear(
    request: Request,
    codigo:                  str   = Form(...),
    descripcion:             str   = Form(""),
    marca_id:                int   = Form(1),
    categoria_id:            int   = Form(1),
    tamano:                  str   = Form(...),
    tipo:                    str   = Form(...),
    potencia:                str   = Form(""),
    precio_venta_mayor_usd:  float = Form(...),
    recargo_bob:             float = Form(80),
    unidad_venta:            str   = Form("par"),
    stock_fisico:            bool  = Form(True),
    cajas_en_stock:          int   = Form(0),
    unidades_por_caja:       int   = Form(0),
    orden:                   int   = Form(0),
    imagenes: List[UploadFile] = File(default=[]),
):
    require_admin(request)
    
    # Validar mínimo 2 imágenes
    imagenes_validas = [img for img in imagenes if img and img.filename]
    if len(imagenes_validas) < 2:
        raise HTTPException(400, "Se requieren mínimo 2 imágenes")

    db = request.app.state.db
    producto_id = None

    if db:
        try:
            async with db.acquire() as c:
                producto_id = await c.fetchval("""
                    INSERT INTO productos
                    (codigo,descripcion,marca_id,categoria_id,tamano,tipo,potencia,
                     precio_venta_mayor_usd,recargo_bob,unidad_venta,stock_fisico,
                     cajas_en_stock,unidades_por_caja,activo,orden,creado_en,actualizado_en)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,TRUE,$14, NOW(), NOW())
                    RETURNING id""",
                    codigo, descripcion, marca_id, categoria_id, tamano, tipo, potencia,
                    precio_venta_mayor_usd, recargo_bob, unidad_venta, stock_fisico,
                    cajas_en_stock, unidades_por_caja, orden)
        except Exception as e:
            raise HTTPException(500, f"Error BD: {e}")
    else:
        producto_id = 9999  # demo

    # Guardar imágenes OPTIMIZADAS
    urls = []
    for idx, img in enumerate(imagenes_validas):
        # Optimizar y guardar
        url = await optimizar_y_guardar_imagen(img, producto_id, idx)
        if url:
            urls.append(url)
            if db and producto_id != 9999:
                try:
                    async with db.acquire() as c:
                        await c.execute("""
                            INSERT INTO imagenes_producto(producto_id, url, orden, es_portada, creado_en)
                            VALUES($1, $2, $3, $4, NOW())
                        """, producto_id, url, idx + 1, idx == 0)
                except Exception as e:
                    print(f"Error guardando imagen en BD: {e}")

    return {"ok": True, "producto_id": producto_id, "imagenes": urls}


# ── Actualizar con optimización de imágenes ──────────────────
@router.put("/{pid}")
async def actualizar(
    pid: int,
    request: Request,
    codigo:                  str   = Form(...),
    descripcion:             str   = Form(""),
    tamano:                  str   = Form(...),
    tipo:                    str   = Form(...),
    potencia:                str   = Form(""),
    precio_venta_mayor_usd:  float = Form(...),
    recargo_bob:             float = Form(80),
    unidad_venta:            str   = Form("par"),
    stock_fisico:            bool  = Form(True),
    cajas_en_stock:          int   = Form(0),
    unidades_por_caja:       int   = Form(0),
    imagenes_nuevas: List[UploadFile] = File(default=[]),
    imagenes_eliminar: str = Form(""),  # JSON array de IDs a eliminar
):
    require_admin(request)
    db = request.app.state.db
    
    if db:
        try:
            async with db.acquire() as c:
                # 1. Actualizar datos del producto
                await c.execute("""
                    UPDATE productos SET
                    codigo=$2, descripcion=$3, tamano=$4, tipo=$5, potencia=$6,
                    precio_venta_mayor_usd=$7, recargo_bob=$8, unidad_venta=$9,
                    stock_fisico=$10, cajas_en_stock=$11, unidades_por_caja=$12,
                    actualizado_en=NOW()
                    WHERE id=$1
                """, pid, codigo, descripcion, tamano, tipo, potencia,
                    precio_venta_mayor_usd, recargo_bob, unidad_venta,
                    stock_fisico, cajas_en_stock, unidades_por_caja)

                # 2. Eliminar imágenes marcadas
                if imagenes_eliminar:
                    ids = json.loads(imagenes_eliminar)
                    for img_id in ids:
                        row = await c.fetchrow("SELECT url FROM imagenes_producto WHERE id=$1 AND producto_id=$2", img_id, pid)
                        if row:
                            await eliminar_imagen(row['url'])
                        await c.execute("DELETE FROM imagenes_producto WHERE id=$1", img_id)

                # 3. Obtener el orden máximo actual
                max_orden = await c.fetchval(
                    "SELECT COALESCE(MAX(orden), 0) FROM imagenes_producto WHERE producto_id=$1", pid
                )

                # 4. Agregar nuevas imágenes OPTIMIZADAS
                for idx, img in enumerate(imagenes_nuevas):
                    if not img.filename:
                        continue
                    
                    nuevo_orden = max_orden + idx + 1
                    url = await optimizar_y_guardar_imagen(img, pid, nuevo_orden)
                    
                    if url:
                        await c.execute("""
                            INSERT INTO imagenes_producto(producto_id, url, orden, es_portada, creado_en)
                            VALUES($1, $2, $3, FALSE, NOW())
                        """, pid, url, nuevo_orden)
                        
        except Exception as e:
            raise HTTPException(500, f"Error BD: {e}")

    return {"ok": True}


# ── Toggle stock ─────────────────────────────────────────────
@router.patch("/{pid}/stock")
async def toggle_stock(pid: int, request: Request):
    require_admin(request)
    db = request.app.state.db
    if db:
        row = await db.fetchrow("SELECT stock_fisico FROM productos WHERE id=$1", pid)
        if not row: raise HTTPException(404)
        nuevo = not row['stock_fisico']
        await db.execute("UPDATE productos SET stock_fisico=$1,actualizado_en=NOW() WHERE id=$2", nuevo, pid)
        return {"ok": True, "stock_fisico": nuevo}
    return {"ok": True, "stock_fisico": True, "demo": True}

# ── Toggle activo (ocultar/mostrar) ──────────────────────────
@router.patch("/{pid}/visibilidad")
async def toggle_visibilidad(pid: int, request: Request):
    require_admin(request)
    db = request.app.state.db
    if db:
        row = await db.fetchrow("SELECT activo FROM productos WHERE id=$1", pid)
        if not row: raise HTTPException(404)
        nuevo = not row['activo']
        await db.execute("UPDATE productos SET activo=$1,actualizado_en=NOW() WHERE id=$2", nuevo, pid)
        return {"ok": True, "activo": nuevo}
    return {"ok": True, "activo": False, "demo": True}

# ── Obtener uno (para editar) ────────────────────────────────
@router.get("/{pid}")
async def obtener(pid: int, request: Request):
    require_admin(request)
    db = request.app.state.db
    if db:
        row = await db.fetchrow("""
            SELECT p.*,
            COALESCE(
                (SELECT json_agg(json_build_object('id',i.id,'url',i.url,'orden',i.orden,'es_portada',i.es_portada)
                 ORDER BY i.orden)
                 FROM imagenes_producto i WHERE i.producto_id=p.id), '[]'
            ) as imagenes
            FROM productos p WHERE p.id=$1""", pid)
        if not row: raise HTTPException(404)
        return dict(row)
    # Demo
    from app.db import DEMO_PRODUCTOS
    p = next((x for x in DEMO_PRODUCTOS if x['id'] == pid), None)
    if not p: raise HTTPException(404)
    return {**p, "imagenes": []}

import os
from datetime import datetime
from decimal import Decimal
DEMO_TC = 10.00

async def get_tc(db) -> float:
    """Obtiene el tipo de cambio activo"""
    if db:
        try:
            r = await db.fetchrow("SELECT valor FROM tipo_cambio WHERE activo=TRUE LIMIT 1")
            if r: 
                return float(r["valor"])
        except Exception as e:
            print(f"Error obteniendo TC: {e}")
    return DEMO_TC

async def get_productos(db) -> list:
    """Obtiene productos SOLO de la base de datos real"""
    if not db:
        print("❌ Error: No hay conexión a la base de datos")
        return []
    
    try:
        rows = await db.fetch("""
            SELECT p.*, m.nombre as marca, c.nombre as categoria,
            ROUND(p.precio_venta_mayor_usd * tc.valor, 2) as precio_mayor_bob,
            ROUND(p.precio_venta_mayor_usd * tc.valor + p.recargo_bob, 2) as precio_minorista_bob,
            tc.valor as tc_activo
            FROM productos p
            JOIN marcas m ON m.id = p.marca_id
            JOIN categorias c ON c.id = p.categoria_id
            CROSS JOIN (SELECT valor FROM tipo_cambio WHERE activo = TRUE LIMIT 1) tc
            WHERE p.activo = TRUE 
            ORDER BY p.orden, p.id
        """)
        
        productos = []
        for row in rows:
            producto = dict(row)
            for key, value in producto.items():
                # Convertir datetime a string
                if isinstance(value, datetime):
                    producto[key] = value.isoformat()
                # Convertir Decimal a float
                elif isinstance(value, Decimal):
                    producto[key] = float(value)
            productos.append(producto)
        
        print(f"✅ Cargados {len(productos)} productos desde la BD")
        return productos
        
    except Exception as e:
        print(f"❌ Error en get_productos: {e}")
        return []

async def get_producto_by_id(db, producto_id: int) -> dict | None:
    """Obtiene un producto por ID"""
    try:
        row = await db.fetchrow("""
            SELECT p.*, m.nombre as marca, c.nombre as categoria
            FROM productos p
            JOIN marcas m ON m.id = p.marca_id
            JOIN categorias c ON c.id = p.categoria_id
            WHERE p.id = $1 AND p.activo = TRUE
        """, producto_id)
        
        if row:
            producto = dict(row)
            for key, value in producto.items():
                if isinstance(value, datetime):
                    producto[key] = value.isoformat()
            return producto
        return None
    except Exception as e:
        print(f"Error obteniendo producto {producto_id}: {e}")
        return None

async def crear_producto(db, producto_data: dict) -> dict:
    """Crea un nuevo producto"""
    try:
        query = """
            INSERT INTO productos (
                codigo, descripcion, marca_id, categoria_id, 
                tamano, tipo, potencia, precio_venta_mayor_usd, 
                recargo_bob, stock_fisico, unidad_venta, orden, activo
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING id
        """
        row = await db.fetchrow(query,
            producto_data.get('codigo'),
            producto_data.get('descripcion'),
            producto_data.get('marca_id'),
            producto_data.get('categoria_id'),
            producto_data.get('tamano'),
            producto_data.get('tipo'),
            producto_data.get('potencia'),
            producto_data.get('precio_venta_mayor_usd'),
            producto_data.get('recargo_bob', 80),
            producto_data.get('stock_fisico', True),
            producto_data.get('unidad_venta', 'unidad'),
            producto_data.get('orden', 999),
            producto_data.get('activo', True)
        )
        return {"id": row["id"], "mensaje": "Producto creado exitosamente"}
    except Exception as e:
        print(f"Error creando producto: {e}")
        raise

async def actualizar_producto(db, producto_id: int, producto_data: dict) -> dict:
    """Actualiza un producto existente"""
    try:
        query = """
            UPDATE productos SET
                codigo = $1, descripcion = $2, marca_id = $3, categoria_id = $4,
                tamano = $5, tipo = $6, potencia = $7, precio_venta_mayor_usd = $8,
                recargo_bob = $9, stock_fisico = $10, unidad_venta = $11, 
                orden = $12, activo = $13, updated_at = NOW()
            WHERE id = $14
        """
        await db.execute(query,
            producto_data.get('codigo'),
            producto_data.get('descripcion'),
            producto_data.get('marca_id'),
            producto_data.get('categoria_id'),
            producto_data.get('tamano'),
            producto_data.get('tipo'),
            producto_data.get('potencia'),
            producto_data.get('precio_venta_mayor_usd'),
            producto_data.get('recargo_bob', 80),
            producto_data.get('stock_fisico', True),
            producto_data.get('unidad_venta', 'unidad'),
            producto_data.get('orden', 999),
            producto_data.get('activo', True),
            producto_id
        )
        return {"mensaje": "Producto actualizado exitosamente"}
    except Exception as e:
        print(f"Error actualizando producto: {e}")
        raise
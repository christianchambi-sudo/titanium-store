DEMO_TC = 10.00

DEMO_PRODUCTOS = [
    {"id":1,"codigo":"TT-400A","descripcion":"Par coaxial 4\" 2 vías, 200W max. Instalación directa en puertas delanteras.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'4"',"tipo":"coaxial","potencia":"200W max","precio_venta_mayor_usd":22.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"par","orden":1},
    {"id":2,"codigo":"TT-400B","descripcion":"Par coaxial 4\" con tweeter integrado, respuesta 50Hz–20kHz.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'4"',"tipo":"coaxial","potencia":"250W max","precio_venta_mayor_usd":28.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"par","orden":2},
    {"id":3,"codigo":"TT-400C","descripcion":"Par coaxial 4\" imán de neodimio, alta sensibilidad 92dB.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'4"',"tipo":"coaxial","potencia":"220W max","precio_venta_mayor_usd":25.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"par","orden":3},
    {"id":4,"codigo":"TT-400D","descripcion":"Par coaxial 4\" serie premium, cono polipropileno tratado.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'4"',"tipo":"coaxial","potencia":"280W max","precio_venta_mayor_usd":32.00,"recargo_bob":80,"stock_fisico":False,"unidad_venta":"par","orden":4},
    {"id":5,"codigo":"TT-525A","descripcion":"Par coaxial 5.25\" 2 vías, armazón de acero estampado.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'5.25"',"tipo":"coaxial","potencia":"250W max","precio_venta_mayor_usd":35.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"par","orden":5},
    {"id":6,"codigo":"TT-525B","descripcion":"Par coaxial 5.25\" serie sport, tweeter de titanio integrado.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'5.25"',"tipo":"coaxial","potencia":"320W max","precio_venta_mayor_usd":42.00,"recargo_bob":80,"stock_fisico":False,"unidad_venta":"par","orden":6},
    {"id":7,"codigo":"TT-650A","descripcion":"Par coaxial 6.5\" 2 vías. El más vendido. Instalación directa.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'6.5"',"tipo":"coaxial","potencia":"300W max","precio_venta_mayor_usd":48.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"par","orden":7},
    {"id":8,"codigo":"TT-650B","descripcion":"Par coaxial 6.5\" tweeter silk dome. Graves profundos.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'6.5"',"tipo":"coaxial","potencia":"360W max","precio_venta_mayor_usd":58.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"par","orden":8},
    {"id":9,"codigo":"TT-650C","descripcion":"Par coaxial 6.5\" serie ultra, cono Kevlar. 35Hz–22kHz.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'6.5"',"tipo":"coaxial","potencia":"400W max","precio_venta_mayor_usd":65.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"par","orden":9},
    {"id":10,"codigo":"TT-650D","descripcion":"Par coaxial 6.5\" diseño sport con rejilla incluida.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'6.5"',"tipo":"coaxial","potencia":"420W max","precio_venta_mayor_usd":72.00,"recargo_bob":80,"stock_fisico":False,"unidad_venta":"par","orden":10},
    {"id":11,"codigo":"TT-650CA","descripcion":"Set componentes 6.5\" — woofer + tweeter separado + crossover. Instalación profesional.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'6.5"',"tipo":"componente","potencia":"350W max","precio_venta_mayor_usd":95.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"set","orden":11},
    {"id":12,"codigo":"TT-650CB","descripcion":"Set componentes 6.5\" serie reference, tweeter cúpula de seda 1\".","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'6.5"',"tipo":"componente","potencia":"480W max","precio_venta_mayor_usd":115.00,"recargo_bob":80,"stock_fisico":False,"unidad_venta":"set","orden":12},
    {"id":13,"codigo":"TT-69A","descripcion":"Par coaxial 6x9\" 3 vías. Potencia de impacto para estante trasero.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'6x9"',"tipo":"coaxial","potencia":"450W max","precio_venta_mayor_usd":65.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"par","orden":13},
    {"id":14,"codigo":"TT-69B","descripcion":"Par coaxial 6x9\" platinum 4 vías. Graves potentes y agudos definidos.","marca":"TITANIUM","categoria":"Parlantes para puerta","tamano":'6x9"',"tipo":"coaxial","potencia":"600W max","precio_venta_mayor_usd":85.00,"recargo_bob":80,"stock_fisico":False,"unidad_venta":"par","orden":14},
    {"id":15,"codigo":"TT-SUB10","descripcion":"Subwoofer activo 10\" con amplificador integrado 300W RMS. Plug & play.","marca":"TITANIUM","categoria":"Bajo activo","tamano":'10"',"tipo":"bajo","potencia":"300W RMS","precio_venta_mayor_usd":185.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"unidad","orden":15},
    {"id":16,"codigo":"TT-BOX65","descripcion":"Parlante 6.5\" en caja de madera MDF. Conecta directo a la radio.","marca":"TITANIUM","categoria":"Parlantes en caja","tamano":'6.5"',"tipo":"caja","potencia":"100W max","precio_venta_mayor_usd":55.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"unidad","orden":16},
    {"id":17,"codigo":"TT-BOX69","descripcion":"Parlante 6x9\" en caja MDF barnizada. Sin instalación.","marca":"TITANIUM","categoria":"Parlantes en caja","tamano":'6x9"',"tipo":"caja","potencia":"150W max","precio_venta_mayor_usd":75.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"unidad","orden":17},
    {"id":18,"codigo":"TT-BOX525D","descripcion":"Doble 5.25\" en caja de madera. Estéreo integrado para camioneta.","marca":"TITANIUM","categoria":"Parlantes en caja","tamano":'5.25"',"tipo":"caja","potencia":"120W max","precio_venta_mayor_usd":65.00,"recargo_bob":80,"stock_fisico":True,"unidad_venta":"unidad","orden":18},
]

def calcular_precios(p: dict, tc: float) -> dict:
    usd = p["precio_venta_mayor_usd"]
    p["precio_mayor_bob"]      = round(usd * tc, 2)
    p["precio_minorista_bob"]  = round(usd * tc + p["recargo_bob"], 2)
    p["tc_activo"] = tc
    return p

async def get_tc(db) -> float:
    if db:
        try:
            r = await db.fetchrow("SELECT valor FROM tipo_cambio WHERE activo=TRUE LIMIT 1")
            if r: return float(r["valor"])
        except: pass
    return DEMO_TC

async def get_productos(db) -> list:
    if db:
        try:
            rows = await db.fetch("""
                SELECT p.*, m.nombre as marca, c.nombre as categoria,
                ROUND(p.precio_venta_mayor_usd * tc.valor,2) as precio_mayor_bob,
                ROUND(p.precio_venta_mayor_usd * tc.valor + p.recargo_bob,2) as precio_minorista_bob,
                tc.valor as tc_activo
                FROM productos p
                JOIN marcas m ON m.id=p.marca_id
                JOIN categorias c ON c.id=p.categoria_id
                CROSS JOIN (SELECT valor FROM tipo_cambio WHERE activo=TRUE LIMIT 1) tc
                WHERE p.activo=TRUE ORDER BY p.orden,p.id""")
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB error: {e}")
    tc = DEMO_TC
    return [calcular_precios(dict(p), tc) for p in DEMO_PRODUCTOS]

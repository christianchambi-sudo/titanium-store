# 🔊 TITANIUM STORE — Sistema de Catálogo y Pedidos

Sistema web completo para gestión de catálogo de parlantes, pedidos por WhatsApp y panel de administración con dos tipos de clientes (mayorista y minorista).

---

## 📁 Estructura del proyecto

```
titanium-store/
├── main.py                         # Entrada principal FastAPI
├── start.sh                        # Script de arranque
├── requirements.txt                # Dependencias Python
├── .env.example                    # Variables de entorno ejemplo
├── app/
│   ├── auth.py                     # Autenticación JWT + bcrypt
│   ├── db.py                       # Conexión BD + datos demo
│   ├── routers/
│   │   ├── catalogo.py             # Rutas catálogo (minorista/mayorista)
│   │   ├── admin.py                # Rutas panel admin
│   │   ├── api.py                  # API REST (TC, productos, pedidos)
│   │   └── pedidos.py              # Rutas de pedidos
│   ├── templates/
│   │   └── pages/
│   │       ├── minorista.html      # 📋 Catálogo público (precios + recargo)
│   │       ├── mayorista.html      # 📋 Catálogo secreto (precios mayor)
│   │       ├── admin_login.html    # 🔐 Login del panel
│   │       └── admin_panel.html    # 🎛️  Panel completo
│   └── static/
│       └── css/
│           └── main.css            # Estilos globales (tema oscuro metálico)
```

---

## 🚀 Instalación y arranque

### 1. Requisitos previos
- Python 3.11+
- PostgreSQL 14+ (opcional — funciona en modo demo sin BD)

### 2. Clonar y configurar

```bash
cd titanium-store
cp .env.example .env
# Editar .env con tus datos
```

### 3. Configurar `.env`

```env
DATABASE_URL=postgresql://usuario:password@localhost:5432/titanium_store
SECRET_KEY=tu_clave_secreta_de_minimo_32_caracteres
WHATSAPP_NUMBER=59170000000
```

### 4. Crear la base de datos PostgreSQL

```bash
psql -U postgres -c "CREATE DATABASE titanium_store;"
psql -U postgres -d titanium_store -f titanium_store_db.sql
```

### 5. Arrancar el servidor

```bash
bash start.sh
# O directamente:
uvicorn main:app --reload --port 8000
```

---

## 🌐 Páginas disponibles

| URL | Descripción | Acceso |
|-----|-------------|--------|
| `/` o `/catalogo` | Catálogo minorista | Público |
| `/mayor/{token}` | Catálogo mayorista | URL secreta |
| `/admin/login` | Login admin | Credenciales |
| `/admin/panel` | Panel completo | Autenticado |

---

## 🔐 Usuarios por defecto (modo demo)

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin123` | Administrador |
| `encargado` | `encarg123` | Encargado |

> ⚠️ **Cambia estas contraseñas** en `app/auth.py` antes de usar en producción.

---

## 💱 Tipo de cambio

El sistema calcula los precios en bolivianos en **tiempo real**:

```
Precio mayorista Bs. = precio_USD × TC_activo
Precio minorista Bs. = precio_USD × TC_activo + recargo_Bs.
```

El TC se actualiza desde el panel admin → Tipo de Cambio. Cada actualización queda registrada con fecha y hora en la tabla `tipo_cambio`.

---

## 🔗 URL mayorista secreta

La URL del catálogo mayorista es única y generada automáticamente:

```
http://tudominio.com/mayor/{token_secreto}
```

- No aparece en buscadores (`noindex,nofollow`)
- No requiere contraseña adicional
- Se genera a partir del `SECRET_KEY` del `.env`
- Para obtenerla: Panel admin → Link Mayorista

---

## 🛒 Flujo de un pedido

```
1. Cliente arma pedido en la web
2. Presiona "Enviar por WhatsApp"
3. Se abre WhatsApp con mensaje completo (productos + precios en Bs. + TC)
4. Tú recibes el pedido y conversas con el cliente
5. Confirmas en: Panel Admin → Pedidos → Confirmar venta ✅
6. El pedido queda registrado con TC, fecha y estado "confirmado"
```

---

## 💰 Sistema de rebajas

**Nivel 1 — Por producto** (en `pedido_detalle`):
- Editas el precio de una línea específica del pedido
- Se guarda precio original y precio rebajado

**Nivel 2 — Descuento global** (en `pedidos`):
- Descuento sobre el total del pedido
- Puede ser monto fijo (Bs.) o porcentaje (%)

---

## 📊 Panel admin — secciones

| Sección | Funciones |
|---------|-----------|
| **Dashboard** | Stats generales, pedidos recientes, gráfico de ventas |
| **Tipo de Cambio** | Actualizar TC, ver historial |
| **Productos** | Ver, editar precios, cambiar stock, agregar productos |
| **Link Mayorista** | Copiar/compartir URL secreta |
| **Pedidos** | Ver, filtrar, confirmar ventas, aplicar rebajas |
| **Clientes** | Registrar, filtrar por departamento, enviar WA |
| **Reportes** | Ventas por mes, por depto, productos top, exportar CSV |
| **Usuarios** | Gestionar accesos al panel admin |

---

## 🔧 Producción — recomendaciones

1. **Nginx** como proxy reverso
2. **SSL/HTTPS** con Let's Encrypt (Certbot)
3. **Gunicorn** en lugar de uvicorn para producción:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```
4. **Variables de entorno** reales en `.env` (nunca commitear)
5. **Backup diario** de PostgreSQL:
   ```bash
   pg_dump titanium_store > backup_$(date +%Y%m%d).sql
   ```
6. **Cambiar contraseñas** de admin en `app/auth.py` o mover a BD

---

## 📱 Compatibilidad

- ✅ Desktop (Chrome, Firefox, Edge, Safari)
- ✅ Mobile (iOS Safari, Android Chrome)
- ✅ Modo demo sin PostgreSQL (datos de prueba incluidos)

---

## 📄 Licencia

Uso interno — TITANIUM STORE Bolivia © 2025

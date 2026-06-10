import os
import io
import secrets
from PIL import Image
from pathlib import Path
from fastapi import UploadFile

# Configuración de la carpeta donde se guardarán las imágenes
UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Tamaño máximo para las imágenes del catálogo (ancho, alto)
TAMANO_MAXIMO = (800, 800)
# Calidad de compresión (80 es un excelente balance entre calidad y peso)
CALIDAD = 80

async def optimizar_y_guardar_imagen(archivo: UploadFile, producto_id: int, orden: int = 0) -> str:
    """
    Recibe un archivo subido, lo optimiza y lo guarda en formato WebP.
    Retorna la URL pública para acceder a la imagen.
    """
    try:
        # 1. Generar un nombre único para la imagen (incluye orden para evitar colisiones)
        nombre_seguro = secrets.token_hex(8)
        nombre_archivo = f"{producto_id}_{orden}_{nombre_seguro}.webp"
        ruta_completa = UPLOAD_DIR / nombre_archivo

        # 2. Leer el contenido del archivo
        contents = await archivo.read()
        
        # 3. Abrir la imagen usando Pillow
        with Image.open(io.BytesIO(contents)) as img:
            # 4. Convertir a RGB (eliminar transparencias si existen)
            if img.mode in ('RGBA', 'LA', 'P'):
                fondo = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    fondo.paste(img, mask=img.split()[-1])
                else:
                    fondo.paste(img)
                img = fondo
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 5. REDIMENSIONAR: mantiene la proporción
            img.thumbnail(TAMANO_MAXIMO, Image.Resampling.LANCZOS)

            # 6. COMPRIMIR y GUARDAR en formato WebP
            img.save(ruta_completa, 'WEBP', quality=CALIDAD, optimize=True)

        # 7. Retornar la URL pública
        return f"/static/uploads/{nombre_archivo}"
    
    except Exception as e:
        print(f"Error optimizando imagen: {e}")
        return None


async def eliminar_imagen(url_imagen: str) -> bool:
    """Elimina una imagen del servidor"""
    if not url_imagen:
        return False
    
    # Extraer el nombre del archivo de la URL
    if url_imagen.startswith("/static/uploads/"):
        nombre_archivo = url_imagen.replace("/static/uploads/", "")
        ruta_completa = UPLOAD_DIR / nombre_archivo
        if ruta_completa.exists():
            ruta_completa.unlink()
            return True
    return False
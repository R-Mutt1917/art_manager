import uuid
import shutil
import re
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings

# Tipos de archivo permitidos
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
MAX_FILE_SIZE = settings.MAX_IMAGE_SIZE  # 5 MB

def limpiar_nombre_archivo(filename: str) -> str:
    """
    Limpia el nombre del archivo eliminando comillas y caracteres problemáticos.
    """
    # Eliminar comillas dobles y simples al inicio y final
    filename = filename.strip('"').strip("'")
    
    # Eliminar cualquier carácter que no sea alfanumérico, guión, guión bajo o punto
    filename = re.sub(r'[^\w\-.]', '_', filename)
    
    return filename

def validar_imagen(file: UploadFile) -> None:
    """
    Valida que el archivo sea una imagen válida y no exceda el tamaño máximo.
    """
    # Validar tipo de archivo
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {file.content_type}. Solo se aceptan: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )
    
    # Validar tamaño (leyendo el archivo en memoria)
    file.file.seek(0, 2)  # Ir al final del archivo
    file_size = file.file.tell()  # Obtener el tamaño
    file.file.seek(0)  # Volver al inicio
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo es demasiado grande ({file_size / 1024 / 1024:.2f} MB). Máximo permitido: {MAX_FILE_SIZE / 1024 / 1024:.2f} MB"
        )

def guardar_imagen(file: UploadFile) -> str:
    """
    Guarda la imagen en la carpeta de uploads con un nombre único.
    Retorna la URL pública de la imagen.
    """
    # Validar el archivo primero
    validar_imagen(file)

    # Limpiar el nombre del archivo para evitar problemas de seguridad
    clean_filename = limpiar_nombre_archivo(file.filename)
    
    # Generar nombre único con UUID para evitar sobrescribir archivos
    file_extension = Path(clean_filename).suffix  # Ej: ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Ruta completa donde se guardará
    file_path = settings.UPLOAD_DIR / unique_filename
    
    # Guardar el archivo
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Retornar la URL pública (relativa al servidor)
    return f"/uploads/{unique_filename}"

def eliminar_imagen(imagen_url: str) -> None:
    """
    Elimina una imagen del sistema de archivos.
    """
    if not imagen_url:
        return
    
    # Extraer el nombre del archivo de la URL
    filename = Path(imagen_url).name
    file_path = settings.UPLOAD_DIR / filename
    
    # Eliminar si existe
    if file_path.exists():
        file_path.unlink()
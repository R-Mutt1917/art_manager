from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime

from app.models.comprador import Comprador
from app.models.obra import Obra, EstadoObra
from app.schemas.comprador import CompradorCreate, CompradorUpdate

class CompradorService:
    def __init__(self, session: Session):
        self.session = session

    def crear_comprador(self, comprador_data: CompradorCreate) -> Comprador:
        """Crea un nuevo comprador."""
        # Validar que no exista un comprador con el mismo email
        if comprador_data.email:
            existente = self.session.exec(
                select(Comprador).where(Comprador.email == comprador_data.email)
            ).first()
            if existente:
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe un comprador con ese email"
                )
        
        db_comprador = Comprador.model_validate(comprador_data)
        self.session.add(db_comprador)
        self.session.commit()
        self.session.refresh(db_comprador)
        return db_comprador

    def obtener_todos(self, activo: Optional[bool] = None) -> List[Comprador]:
        """Obtiene todos los compradores, con filtro opcional por estado."""
        query = select(Comprador)
        if activo is not None:
            query = query.where(Comprador.activo == activo)
        return self.session.exec(query).all()

    def obtener_por_id(self, comprador_id: int) -> Comprador:
        """Obtiene un comprador por ID."""
        comprador = self.session.get(Comprador, comprador_id)
        if not comprador or not comprador.activo:
            raise HTTPException(status_code=404, detail="Comprador no encontrado")
        return comprador

    def actualizar_comprador(self, comprador_id: int, comprador_data: CompradorUpdate) -> Comprador:
        """Actualiza los datos de un comprador."""
        comprador = self.obtener_por_id(comprador_id)
        
        datos_actualizados = comprador_data.model_dump(exclude_unset=True)
        for campo, valor in datos_actualizados.items():
            setattr(comprador, campo, valor)
        
        self.session.add(comprador)
        self.session.commit()
        self.session.refresh(comprador)
        return comprador

    def eliminar_logico(self, comprador_id: int) -> dict:
        """Soft delete de un comprador."""
        comprador = self.session.get(Comprador, comprador_id)
        if not comprador:
            raise HTTPException(status_code=404, detail="Comprador no encontrado")
        
        if not comprador.activo:
            raise HTTPException(status_code=400, detail="El comprador ya fue eliminado")
        
        # Verificar si tiene obras compradas
        obras_asociadas = self.session.exec(
            select(Obra).where(Obra.comprador_id == comprador_id)
        ).all()
        
        if obras_asociadas:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar: el comprador tiene {len(obras_asociadas)} obra(s) asociada(s)"
            )
        
        comprador.activo = False
        self.session.add(comprador)
        self.session.commit()
        
        return {"mensaje": "Comprador dado de baja exitosamente"}

    def obtener_historial_compras(self, comprador_id: int) -> List[dict]:
        """Obtiene todas las obras compradas por un comprador."""
        comprador = self.obtener_por_id(comprador_id)
        
        obras = self.session.exec(
            select(Obra).where(Obra.comprador_id == comprador_id)
        ).all()
        
        return [
            {
                "id": obra.id,
                "titulo": obra.titulo,
                "precio": obra.precio,
                "fecha_venta": obra.fecha_venta,
                "estado": obra.estado.value if hasattr(obra.estado, 'value') else obra.estado
            }
            for obra in obras
        ]

    def registrar_venta(self, obra_id: int, comprador_id: int, fecha_venta: Optional[str] = None) -> dict:
        """
        Registra la venta de una obra a un comprador.
        Actualiza el estado de la obra y la asocia al comprador.
        """
        from datetime import date, datetime
        
        # 1. Verificar que la obra existe
        obra = self.session.get(Obra, obra_id)
        if not obra:
            raise HTTPException(status_code=404, detail="Obra no encontrada")
        
        if obra.estado == EstadoObra.VENDIDA:
            raise HTTPException(status_code=400, detail="La obra ya está vendida")
        
        if obra.estado == EstadoObra.EN_EXPOSICION:
            raise HTTPException(
                status_code=400, 
                detail="La obra está en exposición. Debe ser retirada antes de venderla."
            )
        
        # 2. Verificar que el comprador existe
        comprador = self.session.get(Comprador, comprador_id)
        if not comprador or not comprador.activo:
            raise HTTPException(status_code=404, detail="Comprador no encontrado")
        
        # 3. PROCESAR LA FECHA: Convertir string a objeto date real
        if fecha_venta:
            try:
                fecha_venta_obj = datetime.strptime(fecha_venta, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")
        else:
            fecha_venta_obj = date.today()
        
        # 4. Actualizar la obra
        obra.estado = EstadoObra.VENDIDA
        obra.comprador_id = comprador_id
        obra.fecha_venta = fecha_venta_obj  # Ahora sí es un objeto date válido
        obra.fecha_actualizacion = datetime.utcnow()
        
        self.session.add(obra)
        self.session.commit()
        self.session.refresh(obra)
        
        return {
            "mensaje": "Venta registrada exitosamente",
            "obra_id": obra.id,
            "obra_titulo": obra.titulo,
            "comprador_id": comprador_id,
            "comprador_nombre": comprador.nombre,
            "fecha_venta": str(obra.fecha_venta),
            "precio": obra.precio
        }
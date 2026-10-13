from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.obra import Obra, EstadoObra
from app.schemas.obra import ObraCreate, ObraUpdate

class ObraService:
    """
    Capa de servicio para gestionar la lógica de negocio de Obras.
    Aquí van las reglas de negocio, validaciones complejas, etc.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def obtener_todas(self, estado: Optional[EstadoObra] = None, tecnica_id: Optional[int] = None) -> List[Obra]:
        """Obtiene todas las obras activas con filtros opcionales."""
        query = select(Obra).where(Obra.activo == True)
        
        if estado:
            query = query.where(Obra.estado == estado)
        if tecnica_id:
            query = query.where(Obra.tecnica_id == tecnica_id)
        
        return self.session.exec(query).all()
    
    def obtener_por_id(self, obra_id: int) -> Obra:
        """Obtiene una obra por ID. Lanza 404 si no existe o está eliminada."""
        obra = self.session.get(Obra, obra_id)
        if not obra or not obra.activo:
            raise HTTPException(status_code=404, detail="Obra no encontrada o fue eliminada")
        return obra
    
    def crear(self, obra_data: ObraCreate) -> Obra:
        """Crea una nueva obra con validaciones de negocio."""
        # Validación: Precio no negativo
        if obra_data.precio is not None and obra_data.precio < 0:
            raise HTTPException(status_code=400, detail="El precio no puede ser negativo")
        
        # Validación: Si está vendida, debe tener fecha
        if obra_data.estado == "vendida" and not obra_data.fecha_venta:
            raise HTTPException(
                status_code=400, 
                detail="Una obra vendida debe tener fecha de venta registrada"
            )
        
        db_obra = Obra.model_validate(obra_data)
        self.session.add(db_obra)
        self.session.commit()
        self.session.refresh(db_obra)
        return db_obra
    
    def actualizar(self, obra_id: int, obra_data: ObraUpdate) -> Obra:
        """Actualiza una obra existente."""
        obra = self.obtener_por_id(obra_id)  # Reutilizamos la validación
        
        # Actualizar solo campos proporcionados
        datos_actualizados = obra_data.model_dump(exclude_unset=True)
        for campo, valor in datos_actualizados.items():
            setattr(obra, campo, valor)
        
        obra.fecha_actualizacion = datetime.utcnow()
        self.session.add(obra)
        self.session.commit()
        self.session.refresh(obra)
        return obra
    
    def eliminar_logico(self, obra_id: int) -> dict:
        """
        Soft Delete: Marca la obra como inactiva.
        No la borra físicamente de la base de datos.
        """
        obra = self.session.get(Obra, obra_id)
        
        if not obra:
            raise HTTPException(status_code=404, detail="Obra no encontrada")
        
        if not obra.activo:
            raise HTTPException(status_code=400, detail="La obra ya fue eliminada previamente")
        
        # Aplicar soft delete
        obra.activo = False
        obra.fecha_actualizacion = datetime.utcnow()
        self.session.add(obra)
        self.session.commit()
        
        return {"mensaje": "Obra dada de baja exitosamente (Soft Delete)"}
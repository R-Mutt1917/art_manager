from datetime import datetime
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.obra import Obra, EstadoObra
from app.models.galeria import Galeria
from app.models.artista import Artista
from app.schemas.obra import ObraCreate, ObraUpdate

class ObraService:
    """
    Capa de servicio para gestionar la lógica de negocio de Obras.
    Con aislamiento multi-tenant: todas las queries filtran por galeria_id.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def obtener_todas(
        self,
        galeria: Galeria,  # ← NUEVO: filtrar por tenant
        estado: Optional[EstadoObra] = None, 
        tecnica_id: Optional[int] = None,
        precio_min: Optional[float] = None,
        precio_max: Optional[float] = None,
        busqueda: Optional[str] = None
    ) -> List[Obra]:
        """
        Obtiene obras activas DE LA GALERÍA especificada con filtros avanzados.
        Aislamiento multi-tenant garantizado.
        """
        # 🔒 FILTRO OBLIGATORIO: solo obras de esta galería
        query = select(Obra).where(
            Obra.activo == True,
            Obra.galeria_id == galeria.id,  # ← AISLAMIENTO
        )
        
        if estado:
            query = query.where(Obra.estado == estado)
        if tecnica_id:
            query = query.where(Obra.tecnica_id == tecnica_id)
        if precio_min is not None:
            query = query.where(Obra.precio >= precio_min)
        if precio_max is not None:
            query = query.where(Obra.precio <= precio_max)
        if busqueda:
            termino = f"%{busqueda.lower()}%"
            query = query.where(
                (Obra.titulo.ilike(termino)) | (Obra.notas.ilike(termino))
            )
        
        return self.session.exec(query).all()
    
    def obtener_por_id(self, obra_id: int, galeria: Galeria) -> Obra:  # ← NUEVO: galeria
        """Obtiene una obra por ID. 404 si no existe, fue eliminada o NO pertenece a la galería."""
        obra = self.session.get(Obra, obra_id)
        
        # 🔒 AISLAMIENTO: la obra debe pertenecer a esta galería
        if not obra or not obra.activo or obra.galeria_id != galeria.id:
            raise HTTPException(status_code=404, detail="Obra no encontrada o fue eliminada")
        return obra
    
    def crear(self, obra_data: ObraCreate, galeria: Galeria) -> Obra:  # ← NUEVO: galeria
        """Crea una nueva obra Perteneciente a la galería especificada."""
        if obra_data.precio is not None and obra_data.precio < 0:
            raise HTTPException(status_code=400, detail="El precio no puede ser negativo")
        
        if obra_data.estado == EstadoObra.VENDIDA and not obra_data.fecha_venta:
            raise HTTPException(
                status_code=400, 
                detail="Una obra vendida debe tener fecha de venta registrada"
            )
        
        # Resolver galeria_id y artista_id (con fallback a demo si no vienen)
        galeria_id = obra_data.galeria_id or galeria.id
        artista_id = obra_data.artista_id
        
        # Si no viene artista_id, asignar el artista demo de esta galería
        if artista_id is None:
            artista_demo = self.session.exec(
                select(Artista).where(
                    Artista.galeria_id == galeria.id,
                    Artista.slug == "artista-demo"
                )
            ).first()
            if artista_demo:
                artista_id = artista_demo.id
        
        db_obra = Obra(
            titulo=obra_data.titulo,
            anio=obra_data.anio,
            dimensiones=obra_data.dimensiones,
            precio=obra_data.precio,
            estado=obra_data.estado,
            notas=obra_data.notas,
            tecnica_id=obra_data.tecnica_id,
            comprador_id=obra_data.comprador_id,
            fecha_venta=obra_data.fecha_venta,
            imagen_url=obra_data.imagen_url,
            galeria_id=galeria_id,
            artista_id=artista_id,
        )
        
        self.session.add(db_obra)
        self.session.commit()
        self.session.refresh(db_obra)
        return db_obra
    
    def actualizar(self, obra_id: int, obra_data: ObraUpdate, galeria: Galeria) -> Obra:  # ← NUEVO
        """Actualiza una obra existente (con aislamiento)."""
        obra = self.obtener_por_id(obra_id, galeria)  # ← ya valida galería
        
        datos_actualizados = obra_data.model_dump(exclude_unset=True)
        for campo, valor in datos_actualizados.items():
            setattr(obra, campo, valor)
        
        obra.fecha_actualizacion = datetime.utcnow()
        self.session.add(obra)
        self.session.commit()
        self.session.refresh(obra)
        return obra
    
    def eliminar_logico(self, obra_id: int, galeria: Galeria) -> dict:  # ← NUEVO
        """Soft Delete con aislamiento."""
        obra = self.obtener_por_id(obra_id, galeria)  # ← ya valida galería
        
        obra.activo = False
        obra.fecha_actualizacion = datetime.utcnow()
        self.session.add(obra)
        self.session.commit()
        
        return {"mensaje": "Obra dada de baja exitosamente (Soft Delete)"}
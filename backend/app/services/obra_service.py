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
    Aquí van las reglas de negocio, validaciones complejas, etc.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def obtener_todas(
        self, 
        estado: Optional[EstadoObra] = None, 
        tecnica_id: Optional[int] = None,
        precio_min: Optional[float] = None,
        precio_max: Optional[float] = None,
        busqueda: Optional[str] = None
    ) -> List[Obra]:
        """
        Obtiene todas las obras activas con filtros avanzados.
        
        Filtros disponibles:
        - estado: disponible, vendida, en_exposicion, en_prestamo
        - tecnica_id: ID de la técnica
        - precio_min: precio mínimo (inclusive)
        - precio_max: precio máximo (inclusive)
        - busqueda: búsqueda case-insensitive en título y notas
        """
        query = select(Obra).where(Obra.activo == True)
        
        if estado:
            query = query.where(Obra.estado == estado)
        if tecnica_id:
            query = query.where(Obra.tecnica_id == tecnica_id)
        if precio_min is not None:
            query = query.where(Obra.precio >= precio_min)
        if precio_max is not None:
            query = query.where(Obra.precio <= precio_max)
        if busqueda:
            # Búsqueda case-insensitive en título o notas
            termino = f"%{busqueda.lower()}%"
            query = query.where(
                (Obra.titulo.ilike(termino)) | (Obra.notas.ilike(termino))
            )
        
        return self.session.exec(query).all()
    
    def obtener_por_id(self, obra_id: int) -> Obra:
        """Obtiene una obra por ID. Lanza 404 si no existe o está eliminada."""
        obra = self.session.get(Obra, obra_id)
        if not obra or not obra.activo:
            raise HTTPException(status_code=404, detail="Obra no encontrada o fue eliminada")
        return obra
    
    def crear(self, obra_data: ObraCreate) -> Obra:
        """
        Crea una nueva obra con validaciones de negocio.
        Si no se especifica galeria_id, asigna la Galería Demo automáticamente.
        """
        # Validación: Precio no negativo
        if obra_data.precio is not None and obra_data.precio < 0:
            raise HTTPException(status_code=400, detail="El precio no puede ser negativo")
        
        # Validación: Si está vendida, debe tener fecha
        if obra_data.estado == EstadoObra.VENDIDA and not obra_data.fecha_venta:
            raise HTTPException(
                status_code=400, 
                detail="Una obra vendida debe tener fecha de venta registrada"
            )
        
        # === Multi-tenancy: asignar galería demo si no viene especificada ===
        galeria_id = obra_data.galeria_id
        artista_id = obra_data.artista_id
        
        if galeria_id is None:
            # Buscar Galería Demo
            galeria_demo = self.session.exec(
                select(Galeria).where(Galeria.slug == "galeria-demo")
            ).first()
            
            if galeria_demo:
                galeria_id = galeria_demo.id
                
                # Si no hay artista, asignar Artista Demo
                if artista_id is None:
                    artista_demo = self.session.exec(
                        select(Artista).where(
                            Artista.galeria_id == galeria_demo.id,
                            Artista.slug == "artista-demo"
                        )
                    ).first()
                    if artista_demo:
                        artista_id = artista_demo.id
        # === Fin multi-tenancy ===
        
        # Crear obra con los valores resueltos
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
from datetime import date
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.exposicion import Exposicion
from app.models.obra_exposicion import ObraExposicion
from app.models.galeria import Galeria
from app.schemas.exposicion import ExposicionCreate, AsignarObraSchema
from app.services.obra_service import ObraService

class ExposicionService:
    def __init__(self, session: Session):
        self.session = session
        self.obra_service = ObraService(session)

    def crear_exposicion(self, expo_data: ExposicionCreate, galeria: Galeria) -> Exposicion:
        """Crea una nueva exposición (aislada por galería)."""
        if expo_data.fecha_fin < expo_data.fecha_inicio:
            raise HTTPException(status_code=400, detail="La fecha de fin no puede ser anterior a la de inicio")
        
        db_expo = Exposicion.model_validate(expo_data)
        # TODO en T5C: agregar galeria_id a Exposicion
        self.session.add(db_expo)
        self.session.commit()
        self.session.refresh(db_expo)
        return db_expo

    def asignar_obra_a_exposicion(
        self,
        expo_id: int,
        obra_id: int,
        asignacion_data: AsignarObraSchema,
        galeria: Galeria  # ← NUEVO
    ) -> ObraExposicion:
        """
        Asigna una obra a una exposición VALIDANDO que no haya superposición de fechas.
        Con aislamiento multi-tenant: verifica que la obra pertenece a la galería.
        """
        # 1. Verificar que la exposición existe
        exposicion = self.session.get(Exposicion, expo_id)
        if not exposicion or not exposicion.activa:
            raise HTTPException(status_code=404, detail="Exposición no encontrada o inactiva")

        # 2. Verificar que la obra existe, está activa Y pertenece a esta galería
        obra = self.obra_service.obtener_por_id(obra_id, galeria)  # ← PASAR galeria

        # 3. 🧠 VALIDACIÓN DE FECHAS SUPERPUESTAS
        statement = (
            select(ObraExposicion)
            .join(Exposicion)
            .where(
                ObraExposicion.obra_id == obra_id,
                Exposicion.activa == True,
                Exposicion.fecha_inicio <= exposicion.fecha_fin,
                Exposicion.fecha_fin >= exposicion.fecha_inicio
            )
        )
        
        asignaciones_superpuestas = self.session.exec(statement).all()
        
        asignaciones_en_otra_expo = [a for a in asignaciones_superpuestas if a.exposicion_id != expo_id]
        
        if asignaciones_en_otra_expo:
            raise HTTPException(
                status_code=400, 
                detail=f"La obra '{obra.titulo}' ya está asignada a otra exposición en fechas que se superponen."
            )

        # 4. Verificar si ya está asignada a ESTA MISMA exposición
        ya_asignada_aqui = self.session.exec(
            select(ObraExposicion).where(
                ObraExposicion.obra_id == obra_id,
                ObraExposicion.exposicion_id == expo_id
            )
        ).first()
        
        if ya_asignada_aqui:
            raise HTTPException(status_code=400, detail="La obra ya está asignada a esta exposición")

        # 5. Si todo está bien, creamos la asignación
        nueva_asignacion = ObraExposicion(
            obra_id=obra_id,
            exposicion_id=expo_id,
            sala=asignacion_data.sala,
            pared=asignacion_data.pared
        )
        
        self.session.add(nueva_asignacion)
        self.session.commit()
        self.session.refresh(nueva_asignacion)
        
        return nueva_asignacion

    def obtener_checklist_retiro(self, expo_id: int, galeria: Galeria) -> List[dict]:  # ← NUEVO param
        """
        Genera un checklist de obras que deben ser retiradas al finalizar la exposición.
        Con aislamiento multi-tenant.
        """
        exposicion = self.session.get(Exposicion, expo_id)
        if not exposicion:
            raise HTTPException(status_code=404, detail="Exposición no encontrada")

        statement = select(ObraExposicion).where(ObraExposicion.exposicion_id == expo_id)
        asignaciones = self.session.exec(statement).all()
        
        checklist = []
        for asignacion in asignaciones:
            obra = asignacion.obra
            # 🔒 AISLAMIENTO: solo incluir obras de esta galería
            if obra and obra.galeria_id == galeria.id:
                checklist.append({
                    "titulo_obra": obra.titulo,
                    "dimensiones": obra.dimensiones,
                    "sala": asignacion.sala,
                    "pared": asignacion.pared,
                    "estado_actual": obra.estado.value if hasattr(obra.estado, 'value') else str(obra.estado)
                })
                
        return checklist
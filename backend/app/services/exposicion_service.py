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
        """Crea una nueva exposición perteneciente a la galería."""
        if expo_data.fecha_fin < expo_data.fecha_inicio:
            raise HTTPException(status_code=400, detail="La fecha de fin no puede ser anterior a la de inicio")

        db_expo = Exposicion(
            nombre=expo_data.nombre,
            lugar=expo_data.lugar,
            fecha_inicio=expo_data.fecha_inicio,
            fecha_fin=expo_data.fecha_fin,
            descripcion=expo_data.descripcion,
            galeria_id=galeria.id,  # ← aislamiento (era TODO, ahora implementado)
        )
        self.session.add(db_expo)
        self.session.commit()
        self.session.refresh(db_expo)
        return db_expo

    def obtener_por_id(self, expo_id: int, galeria: Galeria) -> Exposicion:
        """Obtiene una exposición. 404 si no existe o no pertenece a la galería."""
        exposicion = self.session.get(Exposicion, expo_id)
        if not exposicion or exposicion.galeria_id != galeria.id:
            raise HTTPException(status_code=404, detail="Exposición no encontrada")
        return exposicion

    def asignar_obra_a_exposicion(
        self,
        expo_id: int,
        obra_id: int,
        asignacion_data: AsignarObraSchema,
        galeria: Galeria,
    ) -> ObraExposicion:
        """
        Asigna una obra a una exposición VALIDANDO que no haya superposición de fechas.
        Con aislamiento: valida que la exposición Y la obra pertenecen a la galería.
        """
        # 1. Verificar que la exposición existe Y pertenece a esta galería
        exposicion = self.obtener_por_id(expo_id, galeria)  # ← ya valida galería
        if not exposicion.activa:
            raise HTTPException(status_code=404, detail="Exposición inactiva")

        # 2. Verificar que la obra existe, está activa Y pertenece a esta galería
        obra = self.obra_service.obtener_por_id(obra_id, galeria)

        # 3. VALIDACIÓN DE FECHAS SUPERPUESTAS
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

        # 5. Crear la asignación
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

    def obtener_checklist_retiro(self, expo_id: int, galeria: Galeria) -> List[dict]:
        """Genera un checklist de obras que deben ser retiradas. Con aislamiento."""
        # Validar que la exposición pertenece a esta galería
        exposicion = self.obtener_por_id(expo_id, galeria)

        statement = select(ObraExposicion).where(ObraExposicion.exposicion_id == exposicion.id)
        asignaciones = self.session.exec(statement).all()

        checklist = []
        for asignacion in asignaciones:
            obra = asignacion.obra
            # Doble defensa: la obra ya está validada por la galería de la exposición,
            # pero verificamos explícitamente por seguridad.
            if obra and obra.galeria_id == galeria.id:
                checklist.append({
                    "titulo_obra": obra.titulo,
                    "dimensiones": obra.dimensiones,
                    "sala": asignacion.sala,
                    "pared": asignacion.pared,
                    "estado_actual": obra.estado.value if hasattr(obra.estado, 'value') else str(obra.estado)
                })

        return checklist
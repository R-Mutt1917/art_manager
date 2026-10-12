from datetime import datetime, date
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models.prestamo import Prestamo
from app.models.obra import Obra, EstadoObra
from app.schemas.prestamo import PrestamoCreate, DevolucionPrestamo

class PrestamoService:
    def __init__(self, session: Session):
        self.session = session

    def registrar_prestamo(self, prestamo_data: PrestamoCreate) -> Prestamo:
        # 1. Convertir strings a objetos date
        try:
            fecha_prestamo = datetime.strptime(prestamo_data.fecha_prestamo, "%Y-%m-%d").date()
            fecha_devolucion = datetime.strptime(prestamo_data.fecha_devolucion_esperada, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

        if fecha_devolucion < fecha_prestamo:
            raise HTTPException(status_code=400, detail="La fecha de devolución no puede ser anterior a la de préstamo")

        # 2. Verificar la obra
        obra = self.session.get(Obra, prestamo_data.obra_id)
        if not obra:
            raise HTTPException(status_code=404, detail="Obra no encontrada")
        
        if obra.estado == EstadoObra.VENDIDA:
            raise HTTPException(status_code=400, detail="No se puede prestar una obra que ya está vendida")
        
        if obra.estado == EstadoObra.EN_PRESTAMO:
            raise HTTPException(status_code=400, detail="La obra ya está actualmente en préstamo")

        if obra.estado == EstadoObra.EN_EXPOSICION:
            raise HTTPException(status_code=400, detail="La obra está en exposición. Retírela primero.")

        # 3. Crear el préstamo
        nuevo_prestamo = Prestamo(
            obra_id=prestamo_data.obra_id,
            prestatario_nombre=prestamo_data.prestatario_nombre,
            prestatario_contacto=prestamo_data.prestatario_contacto,
            fecha_prestamo=fecha_prestamo,
            fecha_devolucion_esperada=fecha_devolucion,
            motivo=prestamo_data.motivo,
            estado="activo"
        )
        
        # 4. Actualizar estado de la obra
        obra.estado = EstadoObra.EN_PRESTAMO
        obra.fecha_actualizacion = datetime.utcnow()
        
        self.session.add(nuevo_prestamo)
        self.session.add(obra)
        self.session.commit()
        self.session.refresh(nuevo_prestamo)
        
        return nuevo_prestamo

    def registrar_devolucion(self, prestamo_id: int, devolucion_data: DevolucionPrestamo) -> dict:
        # 1. Buscar el préstamo
        prestamo = self.session.get(Prestamo, prestamo_id)
        if not prestamo:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        
        if prestamo.estado == "devuelto":
            raise HTTPException(status_code=400, detail="Este préstamo ya fue registrado como devuelto")

        # 2. Procesar fecha
        try:
            fecha_real = datetime.strptime(devolucion_data.fecha_devolucion_real, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use YYYY-MM-DD")

        # 3. Actualizar préstamo
        prestamo.fecha_devolucion_real = fecha_real
        prestamo.estado = "devuelto"
        
        # 4. Liberar la obra
        obra = self.session.get(Obra, prestamo.obra_id)
        if obra:
            obra.estado = EstadoObra(devolucion_data.estado_obra_tras_devolucion)
            obra.fecha_actualizacion = datetime.utcnow()
            
        self.session.add(prestamo)
        self.session.add(obra)
        self.session.commit()
        
        return {
            "mensaje": "Devolución registrada exitosamente",
            "obra_id": obra.id,
            "nuevo_estado_obra": obra.estado.value
        }

    def obtener_prestamos_activos(self) -> list[Prestamo]:
        """Obtiene todos los préstamos que aún no han sido devueltos."""
        return self.session.exec(
            select(Prestamo).where(Prestamo.estado == "activo")
        ).all()
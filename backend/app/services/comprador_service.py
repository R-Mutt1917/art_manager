from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime

from app.models.comprador import Comprador
from app.models.obra import Obra, EstadoObra
from app.models.galeria import Galeria
from app.schemas.comprador import CompradorCreate, CompradorUpdate

class CompradorService:
    def __init__(self, session: Session):
        self.session = session

    def crear_comprador(self, comprador_data: CompradorCreate, galeria: Galeria) -> Comprador:
        """Crea un nuevo comprador Perteneciente a la galería."""
        # Validar email único DENTRO de la galería (no global)
        if comprador_data.email:
            existente = self.session.exec(
                select(Comprador).where(
                    Comprador.email == comprador_data.email,
                    Comprador.galeria_id == galeria.id,  # ← scope por galería
                    Comprador.activo == True,
                )
            ).first()
            if existente:
                raise HTTPException(
                    status_code=400,
                    detail="Ya existe un comprador con ese email en esta galería"
                )

        db_comprador = Comprador(
            nombre=comprador_data.nombre,
            email=comprador_data.email,
            telefono=comprador_data.telefono,
            direccion=comprador_data.direccion,
            notas=comprador_data.notas,
            galeria_id=galeria.id,  # ← siempre la galería del usuario
        )
        self.session.add(db_comprador)
        self.session.commit()
        self.session.refresh(db_comprador)
        return db_comprador

    def obtener_todos(self, galeria: Galeria, activo: Optional[bool] = None) -> List[Comprador]:
        """Obtiene compradores DE LA GALERÍA especificada, con filtro opcional."""
        query = select(Comprador).where(Comprador.galeria_id == galeria.id)  # ← aislamiento
        if activo is not None:
            query = query.where(Comprador.activo == activo)
        else:
            # Por defecto, solo activos (consistente con soft delete)
            query = query.where(Comprador.activo == True)
        return self.session.exec(query).all()

    def obtener_por_id(self, comprador_id: int, galeria: Galeria) -> Comprador:
        """Obtiene un comprador. 404 si no existe o no pertenece a la galería."""
        comprador = self.session.get(Comprador, comprador_id)
        if not comprador or not comprador.activo or comprador.galeria_id != galeria.id:
            raise HTTPException(status_code=404, detail="Comprador no encontrado")
        return comprador

    def actualizar_comprador(self, comprador_id: int, comprador_data: CompradorUpdate, galeria: Galeria) -> Comprador:
        """Actualiza los datos de un comprador con aislamiento."""
        comprador = self.obtener_por_id(comprador_id, galeria)

        datos_actualizados = comprador_data.model_dump(exclude_unset=True)
        for campo, valor in datos_actualizados.items():
            setattr(comprador, campo, valor)

        self.session.add(comprador)
        self.session.commit()
        self.session.refresh(comprador)
        return comprador

    def eliminar_logico(self, comprador_id: int, galeria: Galeria) -> dict:
        """Soft delete de un comprador con aislamiento."""
        comprador = self.obtener_por_id(comprador_id, galeria)

        # Verificar si tiene obras compradas (solo en esta galería)
        obras_asociadas = self.session.exec(
            select(Obra).where(
                Obra.comprador_id == comprador_id,
                Obra.galeria_id == galeria.id,  # ← aislamiento
            )
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

    def obtener_historial_compras(self, comprador_id: int, galeria: Galeria) -> List[dict]:
        """Obtiene todas las obras compradas por un comprador (con aislamiento)."""
        comprador = self.obtener_por_id(comprador_id, galeria)

        obras = self.session.exec(
            select(Obra).where(
                Obra.comprador_id == comprador_id,
                Obra.galeria_id == galeria.id,  # ← aislamiento defensivo
            )
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

    def registrar_venta(
        self,
        obra_id: int,
        comprador_id: int,
        galeria: Galeria,
        fecha_venta: Optional[str] = None
    ) -> dict:
        """
        Registra la venta de una obra a un comprador.
        Con aislamiento: valida que tanto obra como comprador pertenecen a la galería.
        """
        from datetime import date, datetime

        # 1. Verificar que la obra existe Y pertenece a esta galería
        obra = self.session.get(Obra, obra_id)
        if not obra or obra.galeria_id != galeria.id:
            raise HTTPException(status_code=404, detail="Obra no encontrada")

        if obra.estado == EstadoObra.VENDIDA:
            raise HTTPException(status_code=400, detail="La obra ya está vendida")

        if obra.estado == EstadoObra.EN_EXPOSICION:
            raise HTTPException(
                status_code=400,
                detail="La obra está en exposición. Debe ser retirada antes de venderla."
            )

        # 2. Verificar que el comprador existe Y pertenece a esta galería
        comprador = self.session.get(Comprador, comprador_id)
        if not comprador or not comprador.activo or comprador.galeria_id != galeria.id:
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
        obra.fecha_venta = fecha_venta_obj
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
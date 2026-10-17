from typing import Dict, Any
from sqlmodel import Session, select, func

from app.models.obra import Obra, EstadoObra
from app.models.tecnica import Tecnica


class DashboardService:
    """
    Servicio de métricas agregadas para el dashboard.
    Todas las consultas son de solo lectura y optimizadas con SQL.
    """

    def __init__(self, session: Session):
        self.session = session

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Retorna todas las métricas del dashboard en un solo llamado."""
        # 1. Totales por estado (iteramos los miembros del enum: MAYÚSCULAS)
        obras_por_estado = {}
        for estado in EstadoObra:
            count = self.session.exec(
                select(func.count(Obra.id)).where(
                    Obra.activo == True,
                    Obra.estado == estado,
                )
            ).one()
            obras_por_estado[estado.value] = count  # clave en minúsculas p/ el JSON

        # 2. Total general (solo activas)
        total_obras = sum(obras_por_estado.values())

        # 3. Valor total del inventario (obras disponibles con precio)
        valor_inventario = self.session.exec(
            select(func.coalesce(func.sum(Obra.precio), 0.0)).where(
                Obra.activo == True,
                Obra.estado == EstadoObra.DISPONIBLE,   # ← MAYÚSCULAS
                Obra.precio.isnot(None),
            )
        ).one()

        # 4. Total vendido
        total_vendido = self.session.exec(
            select(func.coalesce(func.sum(Obra.precio), 0.0)).where(
                Obra.activo == True,
                Obra.estado == EstadoObra.VENDIDA,      # ← MAYÚSCULAS
                Obra.precio.isnot(None),
            )
        ).one()

        # 5. Top 5 técnicas por cantidad de obras
        resultados_tecnicas = self.session.exec(
            select(Tecnica.nombre, func.count(Obra.id))
            .join(Obra, Obra.tecnica_id == Tecnica.id)
            .where(Obra.activo == True)
            .group_by(Tecnica.id, Tecnica.nombre)
            .order_by(func.count(Obra.id).desc())
            .limit(5)
        ).all()

        top_tecnicas = [
            {"nombre": nombre, "cantidad": cantidad}
            for nombre, cantidad in resultados_tecnicas
        ]

        return {
            "total_obras": total_obras,
            "obras_por_estado": obras_por_estado,
            "valor_inventario": float(valor_inventario),
            "total_vendido": float(total_vendido),
            "top_tecnicas": top_tecnicas,
        }
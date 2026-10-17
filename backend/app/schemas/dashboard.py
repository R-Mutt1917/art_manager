from typing import Dict, List
from pydantic import BaseModel


class TecnicaCount(BaseModel):
    nombre: str
    cantidad: int


class DashboardStats(BaseModel):
    """Contrato de respuesta de GET /dashboard/stats"""
    total_obras: int
    obras_por_estado: Dict[str, int]
    valor_inventario: float
    total_vendido: float
    top_tecnicas: List[TecnicaCount]
# Importamos en orden de dependencia para evitar errores de SQLModel
from app.models.tecnica import Tecnica
from app.models.comprador import Comprador
from app.models.prestamo import Prestamo
from app.models.exposicion import Exposicion
from app.models.obra_exposicion import ObraExposicion
from app.models.obra import Obra, EstadoObra

__all__ = [
    "Tecnica", "Comprador", "Prestamo", 
    "Exposicion", "ObraExposicion", "Obra", "EstadoObra"
]
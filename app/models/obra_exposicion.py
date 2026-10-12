from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class ObraExposicion(SQLModel, table=True):
    """
    TABLA INTERMEDIA para la relación Muchos a Muchos.
    Permite saber en qué sala o pared está una obra específica dentro de una exposición.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    obra_id: int = Field(foreign_key="obra.id")
    exposicion_id: int = Field(foreign_key="exposicion.id")
    
    # Metadatos de la ubicación física en la muestra
    sala: Optional[str] = Field(default=None, max_length=50)
    pared: Optional[str] = Field(default=None, max_length=50)
    
    # Relaciones
    obra: Optional["Obra"] = Relationship(back_populates="exposiciones")
    exposicion: Optional["Exposicion"] = Relationship(back_populates="obras_en_exposicion")
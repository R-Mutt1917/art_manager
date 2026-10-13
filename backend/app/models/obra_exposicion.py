from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from app.models.obra import Obra
    from app.models.exposicion import Exposicion

class ObraExposicion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    obra_id: int = Field(foreign_key="obra.id")
    exposicion_id: int = Field(foreign_key="exposicion.id")
    sala: Optional[str] = Field(default=None, max_length=50)
    pared: Optional[str] = Field(default=None, max_length=50)
    
    obra: Mapped[Optional["Obra"]] = Relationship(back_populates="exposiciones")
    exposicion: Mapped[Optional["Exposicion"]] = Relationship(back_populates="asignaciones")
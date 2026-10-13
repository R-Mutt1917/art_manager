from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from app.models.obra import Obra

class TecnicaBase(SQLModel):
    nombre: str = Field(index=True, unique=True, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)

class Tecnica(TecnicaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    obras: Mapped[List["Obra"]] = Relationship(back_populates="tecnica")
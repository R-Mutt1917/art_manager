from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# Esto le dice a Python: "Obra existe, confía en mí, no la importes todavía"
if TYPE_CHECKING:
    from app.models.obra import Obra

class TecnicaBase(SQLModel):
    nombre: str = Field(index=True, unique=True, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=500)

class Tecnica(TecnicaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Ahora sí, SQLAlchemy entiende perfectamente que es una lista de "Obra"
    obras: List["Obra"] = Relationship(back_populates="tecnica")
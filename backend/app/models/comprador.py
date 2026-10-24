from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped

if TYPE_CHECKING:
    from app.models.obra import Obra
    from app.models.galeria import Galeria

class Comprador(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=200)
    email: Optional[str] = Field(default=None, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=50)
    direccion: Optional[str] = Field(default=None, max_length=300)
    notas: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)

    # Multi-tenancy: galería a la que pertenece el comprador
    galeria_id: Optional[int] = Field(default=None, foreign_key="galerias.id", index=True)

    obras: Mapped[List["Obra"]] = Relationship(back_populates="comprador")
    galeria: Optional["Galeria"] = Relationship(back_populates="compradores")
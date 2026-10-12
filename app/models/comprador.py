from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Comprador(SQLModel, table=True):
    """Persona o entidad que adquiere las obras."""
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=200)
    email: Optional[str] = Field(default=None, unique=True, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=50)
    notas: Optional[str] = Field(default=None)
    
    # Relación 1:N: Un comprador puede tener muchas obras
    obras: List["Obra"] = Relationship(back_populates="comprador")
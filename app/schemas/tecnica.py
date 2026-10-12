from pydantic import BaseModel, Field
from typing import Optional
from app.models.tecnica import TecnicaBase

class TecnicaCreate(TecnicaBase):
    pass

class TecnicaRead(TecnicaBase):
    id: int
    model_config = {"from_attributes": True}
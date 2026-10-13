from sqlmodel import Session, select
from app.models.tecnica import Tecnica
from app.schemas.tecnica import TecnicaCreate

def crear_tecnica(session: Session, tecnica_data: TecnicaCreate) -> Tecnica:
    """
    Crea una nueva técnica en la base de datos.
    """
    # 1. Convertimos el schema de Pydantic en un modelo de SQLModel
    db_tecnica = Tecnica.model_validate(tecnica_data)
    
    # 2. Lo agregamos a la sesión
    session.add(db_tecnica)
    
    # 3. Guardamos los cambios en la base de datos
    session.commit()
    
    # 4. Refrescamos el objeto para obtener el ID generado automáticamente
    session.refresh(db_tecnica)
    
    return db_tecnica

def obtener_todas_las_tecnicas(session: Session) -> list[Tecnica]:
    """
    Obtiene todas las técnicas registradas.
    """
    statement = select(Tecnica)
    return session.exec(statement).all()
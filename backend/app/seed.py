from sqlmodel import Session
from app.models.tecnica import Tecnica

TECNICAS_COMUNES = [
    {"nombre": "Óleo sobre lienzo", "descripcion": "Pintura al óleo tradicional"},
    {"nombre": "Acrílico sobre lienzo", "descripcion": "Pintura acrílica"},
    {"nombre": "Acuarela sobre papel", "descripcion": "Pintura con agua"},
    {"nombre": "Técnica mixta", "descripcion": "Múltiples técnicas"},
    {"nombre": "Fotografía digital", "descripcion": "Fotografía"},
    {"nombre": "Escultura en bronce", "descripcion": "Escultura"},
    {"nombre": "Dibujo a lápiz", "descripcion": "Grafito"},
]

def seed_database(session: Session):
    """Carga técnicas si no existen."""
    for tecnica_data in TECNICAS_COMUNES:
        existing = session.query(Tecnica).filter(Tecnica.nombre == tecnica_data["nombre"]).first()
        if not existing:
            tecnica = Tecnica(**tecnica_data)
            session.add(tecnica)
    session.commit()
    print(f"✅ Seed completado: {len(TECNICAS_COMUNES)} técnicas cargadas.")
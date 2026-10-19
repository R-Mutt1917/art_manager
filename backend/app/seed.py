from sqlmodel import Session, select    # ← agregar 'select'
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


def seed_admin_user(session: Session):
    """Crea el usuario administrador inicial si no existe (solo desarrollo)."""
    from app.models.usuario import Usuario, RolUsuario
    from app.core.security import hash_password

    existente = session.exec(
        select(Usuario).where(Usuario.email == "admin@artmanager.com")
    ).first()

    if not existente:
        admin = Usuario(
            email="admin@artmanager.com",
            nombre="Administrador",
            rol=RolUsuario.ADMIN,
            password_hash=hash_password("admin123"),
        )
        session.add(admin)
        session.commit()
        print("✅ Seed: usuario admin creado (admin@artmanager.com / admin123)")
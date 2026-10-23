from sqlmodel import Session, select
from app.models.tecnica import Tecnica
from app.models.galeria import Galeria
from app.models.artista import Artista
from app.models.obra import Obra

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

def seed_galeria_demo(session: Session) -> Galeria:
    """
    Crea la Galería Demo por defecto si no existe.
    Esta galería es el "tenant inicial" para todas las obras
    que se crearon antes del sistema multi-tenant.
    
    En Fase 3 (multi-tenancy real), cada usuario pertenecerá
    a su propia galería, pero por ahora usamos esta demo.
    """
    # Verificar si ya existe
    galeria = session.exec(
        select(Galeria).where(Galeria.slug == "galeria-demo")
    ).first()
    
    if galeria:
        return galeria
    
    # Crear galería demo
    galeria = Galeria(
        nombre="Galería Demo",
        slug="galeria-demo",
        bio="Galería de demostración para desarrollo y testing.",
        ubicacion="Buenos Aires, Argentina",
        sitio_web="https://artmanager.com",
    )
    session.add(galeria)
    session.commit()
    session.refresh(galeria)
    
    print("✅ Seed: Galería Demo creada (galeria-demo)")
    return galeria

def seed_artista_demo(session: Session, galeria: Galeria) -> Artista:
    """
    Crea un Artista Demo por defecto en la galería especificada.
    """
    # Verificar si ya existe
    artista = session.exec(
        select(Artista).where(
            Artista.galeria_id == galeria.id,
            Artista.slug == "artista-demo"
        )
    ).first()
    
    if artista:
        return artista
    
    # Crear artista demo
    artista = Artista(
        galeria_id=galeria.id,
        nombre="Artista Demo",
        slug="artista-demo",
        bio="Artista de demostración para desarrollo y testing.",
        nacionalidad="Argentina",
        anio_nacimiento=1990,
    )
    session.add(artista)
    session.commit()
    session.refresh(artista)
    
    print("✅ Seed: Artista Demo creado (artista-demo)")
    return artista

def migrar_obras_a_galeria_demo(session: Session, galeria: Galeria, artista: Artista):
    """
    Migra todas las obras que no tienen galeria_id asignándolas
    a la Galería Demo. Esto es necesario para obras creadas antes
    del sistema multi-tenant.
    
    Una vez migradas, todas las obras tienen un tenant válido.
    """
    obras_sin_galeria = session.exec(
        select(Obra).where(Obra.galeria_id == None)
    ).all()
    
    if not obras_sin_galeria:
        return
    
    for obra in obras_sin_galeria:
        obra.galeria_id = galeria.id
        obra.artista_id = artista.id
        session.add(obra)
    
    session.commit()
    print(f"✅ Migración: {len(obras_sin_galeria)} obras asignadas a Galería Demo")
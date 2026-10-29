import os
from sqlmodel import Session, select
from app.models.tecnica import Tecnica
from app.models.galeria import Galeria
from app.models.artista import Artista
from app.models.obra import Obra
from app.models.usuario import UserAccount, UserGalleryRole, RolUsuario
from app.core.security import hash_password

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
    for tecnica_data in TECNICAS_COMUNES:
        existing = session.query(Tecnica).filter(Tecnica.nombre == tecnica_data["nombre"]).first()
        if not existing:
            tecnica = Tecnica(**tecnica_data)
            session.add(tecnica)
    session.commit()
    print(f"✅ Seed completado: {len(TECNICAS_COMUNES)} técnicas cargadas.")

def seed_admin_user(session: Session):
    existente = session.exec(
        select(UserAccount).where(UserAccount.email == "admin@artmanager.com")
    ).first()

    if not existente:
        admin = UserAccount(
            email="admin@artmanager.com",
            nombre="Super Administrador",
            password_hash=hash_password("admin123"),
        )
        session.add(admin)
        session.commit()
        print("✅ Seed: Super Admin creado (admin@artmanager.com / admin123)")

def seed_galeria_demo(session: Session) -> Galeria:
    galeria = session.exec(
        select(Galeria).where(Galeria.slug == "galeria-demo")
    ).first()

    if galeria:
        return galeria

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
    artista = session.exec(
        select(Artista).where(
            Artista.galeria_id == galeria.id,
            Artista.slug == "artista-demo"
        )
    ).first()

    if artista:
        return artista

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

def seed_dev_users(session: Session):
    """
    Crea cuentas demo con roles por galería (SOLO development).
    Además vincula al super admin a la Galería Demo para que pueda operar.
    Password común: demo1234
    """
    from app.models.usuario import UserAccount, UserGalleryRole, RolUsuario
    from app.core.security import hash_password

    galeria = session.exec(
        select(Galeria).where(Galeria.slug == "galeria-demo")
    ).first()
    if not galeria:
        return

    # ← NUEVO: el super admin necesita galería activa + rol para poder operar
    super_admin = session.exec(
        select(UserAccount).where(UserAccount.email == "admin@artmanager.com")
    ).first()
    if super_admin:
        if super_admin.galeria_id_activa is None:
            super_admin.galeria_id_activa = galeria.id
            session.add(super_admin)
        tiene_rol = session.exec(
            select(UserGalleryRole).where(
                UserGalleryRole.user_id == super_admin.id,
                UserGalleryRole.galeria_id == galeria.id,
            )
        ).first()
        if not tiene_rol:
            session.add(UserGalleryRole(
                user_id=super_admin.id,
                galeria_id=galeria.id,
                rol=RolUsuario.ADMIN,
            ))
        session.commit()
        print("✅ Seed: super admin vinculado a Galería Demo (rol ADMIN)")

    dev_users = [
        ("dueno@demo.com",   "Dueño de Galería",  RolUsuario.ADMIN),
        ("curador@demo.com", "Curador Demo",      RolUsuario.CURADOR),
        ("asesor@demo.com",  "Asesor Comercial",  RolUsuario.ASESOR),
        ("viewer@demo.com",  "Visitante Interno", RolUsuario.VIEWER),
    ]

    creados = 0
    for email, nombre, rol in dev_users:
        user = session.exec(select(UserAccount).where(UserAccount.email == email)).first()
        if not user:
            user = UserAccount(
                email=email,
                nombre=nombre,
                password_hash=hash_password("demo1234"),
                galeria_id_activa=galeria.id,
            )
            session.add(user)
            session.flush()
            session.add(UserGalleryRole(
                user_id=user.id,
                galeria_id=galeria.id,
                rol=rol
            ))
            creados += 1

    if creados:
        session.commit()
        print(f"✅ Seed: {creados} cuentas de usuario con roles asignados en Galería Demo (pass: demo1234)")

def seed_multitenancy(session: Session):
    galeria = seed_galeria_demo(session)
    artista = seed_artista_demo(session, galeria)
    migrar_obras_a_galeria_demo(session, galeria, artista)
    # Nota: Ya no necesitamos "asignar_galeria_demo_a_usuarios" masivo, 
    # porque seed_dev_users lo hace de forma granular con UserGalleryRole.
import re
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.galeria import Galeria
from app.models.usuario import UserAccount, UserGalleryRole, RolUsuario
from app.core.security import hash_password, create_access_token, create_refresh_token

def _slugify(text: str) -> str:
    """Convierte texto a slug URL-friendly."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text

def _generar_slug_unico(session: Session, nombre: str) -> str:
    """Genera un slug único para la galería, agregando sufijo numérico si es necesario."""
    base_slug = _slugify(nombre)
    slug = base_slug
    counter = 1

    while session.exec(select(Galeria).where(Galeria.slug == slug)).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

class GaleriaService:
    def __init__(self, session: Session):
        self.session = session

    def registrar_galeria(
        self,
        nombre_galeria: str,
        email_dueno: str,
        nombre_dueno: str,
        password_dueno: str,
        bio_galeria: str | None = None,
        ubicacion_galeria: str | None = None,
        sitio_web_galeria: str | None = None,
    ) -> dict:
        """
        Registra una nueva galería + su dueño (ADMIN) en una transacción atómica.
        
        Returns:
            dict con galeria_id, user_id, access_token, refresh_token
        """
        # 1. Validar email único
        user_existente = self.session.exec(
            select(UserAccount).where(UserAccount.email == email_dueno)
        ).first()
        if user_existente:
            raise HTTPException(
                status_code=409,
                detail=f"El email {email_dueno} ya está registrado"
            )

        # 2. Generar slug único
        slug = _generar_slug_unico(self.session, nombre_galeria)

        # 3. Crear UserAccount (sin rol global, los roles son por galería)
        user = UserAccount(
            email=email_dueno,
            nombre=nombre_dueno,
            password_hash=hash_password(password_dueno),
        )
        self.session.add(user)
        self.session.flush()  # Para obtener user.id

        # 4. Crear Galeria
        galeria = Galeria(
            nombre=nombre_galeria,
            slug=slug,
            bio=bio_galeria,
            ubicacion=ubicacion_galeria,
            sitio_web=sitio_web_galeria,
            activo=True,
        )
        self.session.add(galeria)
        self.session.flush()  # Para obtener galeria.id

        # 5. Asignar rol ADMIN al dueño en esta galería
        rol_admin = UserGalleryRole(
            user_id=user.id,
            galeria_id=galeria.id,
            rol=RolUsuario.ADMIN,
        )
        self.session.add(rol_admin)

        # 6. Setear galería activa
        user.galeria_id_activa = galeria.id
        self.session.add(user)

        # 7. Commit atómico
        self.session.commit()
        self.session.refresh(user)
        self.session.refresh(galeria)

        # 8. Generar tokens
        access_token = create_access_token(user.id, RolUsuario.ADMIN.value)
        refresh_token = create_refresh_token(user.id, RolUsuario.ADMIN.value)

        return {
            "galeria_id": galeria.id,
            "galeria_nombre": galeria.nombre,
            "galeria_slug": galeria.slug,
            "user_id": user.id,
            "user_email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User


def seed_default_admin(db: Session) -> None:
    existing_admin = db.query(User).filter(User.email == settings.seed_admin_email).first()
    if existing_admin:
        return

    admin = User(
        email=settings.seed_admin_email,
        hashed_password=hash_password(settings.seed_admin_password),
        role="admin",
        department=settings.seed_admin_department,
    )
    db.add(admin)
    db.commit()

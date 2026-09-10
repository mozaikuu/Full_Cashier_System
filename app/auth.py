import hashlib
import secrets

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Cashier, Setting

DEFAULT_PASSWORD = "1234"
DEFAULT_RECOVERY_CODE = "SANDY-RESET"


def _hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180000).hex()
    return f"{salt}${digest}"


def _matches(password: str, stored: str) -> bool:
    try:
        salt, expected = stored.split("$", 1)
    except ValueError:
        return False
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 180000).hex()
    return secrets.compare_digest(actual, expected)


def initialize_auth() -> None:
    with SessionLocal.begin() as session:
        if session.get(Setting, "admin_password_hash") is None:
            session.add(Setting(key="admin_password_hash", value=_hash_password(DEFAULT_PASSWORD)))
        if session.get(Setting, "admin_recovery_code") is None:
            session.add(Setting(key="admin_recovery_code", value=DEFAULT_RECOVERY_CODE))


def authenticate(password: str, username: str | None = None) -> bool:
    if username is not None:
        return authenticate_user(username, password) is not None
    with SessionLocal() as session:
        setting = session.get(Setting, "admin_password_hash")
        return bool(setting and _matches(password, setting.value))


def authenticate_user(username: str, password: str) -> dict[str, str] | None:
    normalized = username.strip().lower()
    if normalized == "admin":
        return {"username": "admin", "role": "admin"} if authenticate(password) else None
    with SessionLocal() as session:
        cashier = session.scalar(select(Cashier).where(Cashier.username == normalized, Cashier.is_active.is_(True)))
        if cashier and _matches(password, cashier.password_hash):
            return {"username": cashier.username, "role": "cashier"}
    return None


def list_cashiers() -> list[Cashier]:
    with SessionLocal() as session:
        return list(session.scalars(select(Cashier).order_by(Cashier.username)).all())


def create_cashier(username: str, password: str) -> None:
    normalized = username.strip().lower()
    if not normalized or normalized == "admin" or len(password) < 4:
        raise ValueError("اكتب اسم مستخدم صالح وكلمة سر من 4 أحرف على الأقل")
    with SessionLocal.begin() as session:
        if session.scalar(select(Cashier).where(Cashier.username == normalized)):
            raise ValueError("اسم المستخدم موجود بالفعل")
        session.add(Cashier(username=normalized, password_hash=_hash_password(password)))


def set_cashier_active(cashier_id: int, active: bool) -> None:
    with SessionLocal.begin() as session:
        cashier = session.get(Cashier, cashier_id)
        if cashier:
            cashier.is_active = active


def change_cashier_password(username: str, old_password: str, new_password: str) -> bool:
    if len(new_password) < 4:
        return False
    with SessionLocal.begin() as session:
        cashier = session.scalar(select(Cashier).where(Cashier.username == username.strip().lower(), Cashier.is_active.is_(True)))
        if not cashier or not _matches(old_password, cashier.password_hash):
            return False
        cashier.password_hash = _hash_password(new_password)
        return True


def change_password(old_password: str, new_password: str) -> bool:
    if len(new_password) < 4 or not authenticate(old_password):
        return False
    with SessionLocal.begin() as session:
        session.merge(Setting(key="admin_password_hash", value=_hash_password(new_password)))
        return True


def reset_password(recovery_code: str, new_password: str) -> bool:
    if len(new_password) < 4:
        return False
    with SessionLocal.begin() as session:
        recovery = session.get(Setting, "admin_recovery_code")
        if not recovery or not secrets.compare_digest(recovery_code.strip(), recovery.value):
            return False
        session.merge(Setting(key="admin_password_hash", value=_hash_password(new_password)))
        return True
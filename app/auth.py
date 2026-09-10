import hashlib
import secrets

from app.database import SessionLocal
from app.models import Setting

DEFAULT_PASSWORD = "1234"
DEFAULT_RECOVERY_CODE = "MOUSSA-RESET"


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


def authenticate(password: str) -> bool:
    with SessionLocal() as session:
        setting = session.get(Setting, "admin_password_hash")
        return bool(setting and _matches(password, setting.value))


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
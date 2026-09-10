from pathlib import Path
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
DATA_DIR = APP_DIR / "data"
DATABASE_URL = f"sqlite:///{DATA_DIR / 'moussa_cashier.db'}"


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    from app import models  # noqa: F401
    Base.metadata.create_all(engine)
    columns = {column["name"] for column in inspect(engine).get_columns("sales")}
    with engine.begin() as connection:
        if "buyer_name" not in columns:
            connection.execute(text("ALTER TABLE sales ADD COLUMN buyer_name VARCHAR(160) NOT NULL DEFAULT ''"))
        if "buyer_phone" not in columns:
            connection.execute(text("ALTER TABLE sales ADD COLUMN buyer_phone VARCHAR(40) NOT NULL DEFAULT ''"))
    with SessionLocal.begin() as session:
        defaults = {
            "store_name": "fyonka",
            "store_address": "baltim",
            "store_phone": "01201538851",
            "currency": "EGP",
            "tax_rate": "0",
            "receipt_printer": "",
            "label_printer": "",
            "language": "ar",
        }
        for key, value in defaults.items():
            if session.get(models.Setting, key) is None:
                session.add(models.Setting(key=key, value=value))


def factory_reset() -> None:
    from app import models

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    init_db()

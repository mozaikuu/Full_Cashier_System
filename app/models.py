from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    subcategories: Mapped[list["Subcategory"]] = relationship(cascade="all, delete-orphan")


class Subcategory(Base):
    __tablename__ = "subcategories"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120))
    sort_order: Mapped[int] = mapped_column(default=0)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    description: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    store_id: Mapped[int] = mapped_column(default=1)
    variants: Mapped[list["Variant"]] = relationship(cascade="all, delete-orphan")
    categories: Mapped[list["ProductCategoryLink"]] = relationship(cascade="all, delete-orphan")


class ProductCategoryLink(Base):
    __tablename__ = "product_category_links"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    subcategory_id: Mapped[int | None] = mapped_column(ForeignKey("subcategories.id"), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    __table_args__ = (UniqueConstraint("product_id", "category_id", "subcategory_id"),)


class Variant(Base):
    __tablename__ = "product_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    sku: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    stock_qty: Mapped[int] = mapped_column(default=0)
    reorder_level: Mapped[int] = mapped_column(default=0)
    attributes_json: Mapped[str] = mapped_column(Text, default="{}")
    product: Mapped[Product] = relationship()


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"))
    qty_change: Mapped[int] = mapped_column()
    reason: Mapped[str] = mapped_column(String(30))
    reference_id: Mapped[str] = mapped_column(String(80), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    variant: Mapped[Variant] = relationship()


class Sale(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    payment_method: Mapped[str] = mapped_column(String(30), default="cash")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    store_id: Mapped[int] = mapped_column(default=1)
    buyer_name: Mapped[str] = mapped_column(String(160), default="")
    buyer_phone: Mapped[str] = mapped_column(String(40), default="")
    lines: Mapped[list["SaleLine"]] = relationship(cascade="all, delete-orphan")


class SaleLine(Base):
    __tablename__ = "sale_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"))
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"))
    qty: Mapped[int] = mapped_column()
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    line_total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    variant: Mapped[Variant] = relationship()


class Setting(Base):
    __tablename__ = "settings"
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")

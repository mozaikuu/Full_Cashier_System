from datetime import datetime, time
from decimal import Decimal
from sqlalchemy import func, or_, select
from app.database import SessionLocal
from app.models import Category, Product, ProductCategoryLink, Sale, SaleLine, Setting, StockMovement, Variant


def money(value: Decimal | int | float) -> str:
    return f"EGP {Decimal(str(value or 0)):,.2f}"


class CategoryService:
    @staticmethod
    def list():
        with SessionLocal() as session:
            return session.scalars(select(Category).order_by(Category.sort_order, Category.name)).all()

    @staticmethod
    def save(name: str, sort_order: int = 0, category_id: int | None = None):
        with SessionLocal.begin() as session:
            category = session.get(Category, category_id) if category_id else Category()
            category.name, category.sort_order = name.strip(), sort_order
            session.add(category)


class ProductService:
    @staticmethod
    def search(term: str = ""):
        with SessionLocal() as session:
            query = select(Variant).join(Variant.product).where(Product.is_active.is_(True))
            if term.strip():
                like = f"%{term.strip()}%"
                query = query.where(or_(Product.name.ilike(like), Variant.barcode.ilike(like), Variant.sku.ilike(like)))
            return session.scalars(query.order_by(Product.name)).all()

    @staticmethod
    def create(name: str, sku: str, barcode: str, price: Decimal, cost: Decimal, stock: int, reorder: int, category_id: int):
        with SessionLocal.begin() as session:
            product = Product(name=name.strip())
            product.variants.append(Variant(sku=sku.strip(), barcode=barcode.strip(), price=price, cost=cost, stock_qty=stock, reorder_level=reorder))
            product.categories.append(ProductCategoryLink(category_id=category_id, is_primary=True))
            session.add(product)
            session.flush()
            if stock:
                session.add(StockMovement(variant_id=product.variants[0].id, qty_change=stock, reason="restock"))


class InventoryService:
    @staticmethod
    def adjust(variant_id: int, quantity: int, reason: str):
        with SessionLocal.begin() as session:
            variant = session.get(Variant, variant_id)
            if not variant:
                raise ValueError("Variant not found")
            new_quantity = quantity if reason == "adjustment" else variant.stock_qty + quantity
            if new_quantity < 0:
                raise ValueError("Stock cannot be negative")
            delta = new_quantity - variant.stock_qty
            variant.stock_qty = new_quantity
            session.add(StockMovement(variant_id=variant_id, qty_change=delta, reason=reason))


class SaleService:
    @staticmethod
    def checkout(items: dict[int, int]) -> Sale:
        with SessionLocal.begin() as session:
            variants = {variant_id: session.get(Variant, variant_id) for variant_id in items}
            if any(not variant for variant in variants.values()):
                raise ValueError("Product not found")
            if any(variants[key].stock_qty < qty for key, qty in items.items()):
                raise ValueError("Insufficient stock")
            sale = Sale(payment_method="cash")
            total = Decimal("0")
            session.add(sale)
            session.flush()
            for variant_id, qty in items.items():
                variant = variants[variant_id]
                variant.product = session.get(Product, variant.product_id)
                line_total = Decimal(variant.price) * qty
                total += line_total
                variant.stock_qty -= qty
                sale.lines.append(SaleLine(variant=variant, qty=qty, unit_price=variant.price, line_total=line_total))
                session.add(StockMovement(variant_id=variant.id, qty_change=-qty, reason="sale", reference_id=str(sale.id)))
            sale.total = total
            return sale


class ReportService:
    @staticmethod
    def today():
        start = datetime.combine(datetime.today(), time.min)
        with SessionLocal() as session:
            total = session.scalar(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.created_at >= start))
            count = session.scalar(select(func.count(Sale.id)).where(Sale.created_at >= start))
            low = session.scalar(select(func.count(Variant.id)).where(Variant.stock_qty <= Variant.reorder_level, Variant.reorder_level > 0))
            return Decimal(str(total or 0)), count or 0, low or 0


def settings() -> dict[str, str]:
    with SessionLocal() as session:
        return {row.key: row.value for row in session.scalars(select(Setting)).all()}

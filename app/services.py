from datetime import datetime, time
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models import Category, Product, ProductCategoryLink, Sale, SaleLine, Setting, StockMovement, Variant


def money(value: Decimal | int | float) -> str:
    return f"EGP {Decimal(str(value or 0)):,.2f}"


def _ean13(value: int) -> str:
    body = f"200{value:09d}"[-12:]
    checksum = (10 - sum((1 if index % 2 == 0 else 3) * int(digit) for index, digit in enumerate(body)) % 10) % 10
    return body + str(checksum)


def generate_sku(product_id: int) -> str:
    return f"PRD-{product_id:06d}"


def generate_barcode(product_id: int) -> str:
    return f"{20000000 + product_id:08d}"


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

    @staticmethod
    def delete(category_id: int):
        with SessionLocal.begin() as session:
            category = session.get(Category, category_id)
            if category:
                if session.scalar(select(func.count(ProductCategoryLink.id)).where(ProductCategoryLink.category_id == category_id)):
                    raise ValueError("لا يمكن حذف تصنيف مرتبط بمنتجات")
                session.delete(category)

class ProductService:
    @staticmethod
    def search(term: str = "", category_id: int | None = None):
        with SessionLocal() as session:
            query = select(Variant).options(joinedload(Variant.product)).join(Variant.product).where(Product.is_active.is_(True))
            if term.strip():
                like = f"%{term.strip()}%"
                query = query.where(or_(Product.name.ilike(like), Variant.barcode.ilike(like), Variant.sku.ilike(like)))
            if category_id:
                query = query.join(ProductCategoryLink).where(ProductCategoryLink.category_id == category_id)
            return session.scalars(query.order_by(Product.name)).all()

    @staticmethod
    def categories(product_id: int):
        with SessionLocal() as session:
            return session.scalars(select(ProductCategoryLink).where(ProductCategoryLink.product_id == product_id)).all()

    @staticmethod
    def create(name: str, sku: str, barcode: str, price: Decimal, cost: Decimal, stock: int, reorder: int, category_id: int):
        with SessionLocal.begin() as session:
            product = Product(name=name.strip())
            temporary_id = uuid4().hex
            requested_sku = sku.strip()
            requested_barcode = barcode.strip()
            variant = Variant(sku=requested_sku or f"TEMP-{temporary_id}", barcode=requested_barcode or f"TEMP-{temporary_id}", price=price, cost=cost, stock_qty=stock, reorder_level=reorder)
            product.variants.append(variant)
            product.categories.append(ProductCategoryLink(category_id=category_id, is_primary=True))
            session.add(product)
            session.flush()
            variant.sku = requested_sku or generate_sku(product.id)
            variant.barcode = requested_barcode or generate_barcode(product.id)
            if stock:
                session.add(StockMovement(variant_id=product.variants[0].id, qty_change=stock, reason="restock"))
            return variant

    @staticmethod
    def update(product_id: int, name: str, sku: str, barcode: str, price: Decimal, cost: Decimal, stock: int, reorder: int, category_ids: list[int]):
        if not category_ids:
            raise ValueError("يجب اختيار تصنيف واحد على الأقل")
        with SessionLocal.begin() as session:
            product = session.get(Product, product_id)
            if not product or not product.variants:
                raise ValueError("المنتج غير موجود")
            variant = product.variants[0]
            product.name, variant.sku, variant.barcode = name.strip(), sku.strip(), barcode.strip()
            variant.price, variant.cost, variant.reorder_level = price, cost, reorder
            if stock < 0:
                raise ValueError("الكمية مينفعش تكون بالسالب")
            if stock != variant.stock_qty:
                delta = stock - variant.stock_qty
                variant.stock_qty = stock
                session.add(StockMovement(variant_id=variant.id, qty_change=delta, reason="adjustment"))
            product.categories.clear()
            product.categories.extend(ProductCategoryLink(category_id=category_id, is_primary=index == 0) for index, category_id in enumerate(category_ids))

    @staticmethod
    def delete(product_id: int):
        with SessionLocal.begin() as session:
            product = session.get(Product, product_id)
            if product:
                product.is_active = False


class InventoryService:
    @staticmethod
    def set_reorder_level(variant_id: int, reorder_level: int):
        if reorder_level < 0:
            raise ValueError("حد الطلب مينفعش يكون بالسالب")
        with SessionLocal.begin() as session:
            variant = session.get(Variant, variant_id)
            if not variant:
                raise ValueError("الصنف غير موجود")
            variant.reorder_level = reorder_level

    @staticmethod
    def adjust(variant_id: int, quantity: int, reason: str):
        with SessionLocal.begin() as session:
            variant = session.get(Variant, variant_id)
            if not variant:
                raise ValueError("الصنف غير موجود")
            new_quantity = quantity if reason == "adjustment" else variant.stock_qty + quantity
            if new_quantity < 0:
                raise ValueError("الكمية مينفعش تكون بالسالب")
            delta = new_quantity - variant.stock_qty
            variant.stock_qty = new_quantity
            session.add(StockMovement(variant_id=variant_id, qty_change=delta, reason=reason))

    @staticmethod
    def movements(variant_id: int | None = None):
        with SessionLocal() as session:
            query = select(StockMovement).options(joinedload(StockMovement.variant)).order_by(StockMovement.created_at.desc())
            if variant_id:
                query = query.where(StockMovement.variant_id == variant_id)
            return session.scalars(query).all()


class SaleService:
    @staticmethod
    def list_sales(include_archived: bool = False):
        with SessionLocal() as session:
            query = select(Sale).options(joinedload(Sale.lines).joinedload(SaleLine.variant).joinedload(Variant.product))
            if not include_archived:
                query = query.where(Sale.archived.is_(False))
            return session.scalars(query.order_by(Sale.created_at.desc())).unique().all()

    @staticmethod
    def archive_or_delete_sale(sale_id: int, restore_stock: bool = False):
        with SessionLocal.begin() as session:
            sale = session.get(Sale, sale_id)
            if not sale:
                raise ValueError("الفاتورة مش موجودة")
            if sale.archived:
                session.delete(sale)
                return "deleted"
            sale.archived = True
            if restore_stock and not sale.stock_restored:
                for line in sale.lines:
                    variant = session.get(Variant, line.variant_id)
                    if variant:
                        variant.stock_qty += line.qty
                        session.add(StockMovement(variant_id=variant.id, qty_change=line.qty, reason="sale_archive_restore", reference_id=str(sale.id)))
                sale.stock_restored = True
            return "archived"

    @staticmethod
    def delete_sale(sale_id: int):
        return SaleService.archive_or_delete_sale(sale_id)

    @staticmethod
    def checkout(items: dict[int, int], cash_received: Decimal, buyer_name: str = "", buyer_phone: str = "", cashier_username: str = "admin") -> tuple[Sale, Decimal]:
        with SessionLocal.begin() as session:
            if not items or any(quantity <= 0 for quantity in items.values()):
                raise ValueError("سلة المشتريات فارغة")
            variants = {variant_id: session.get(Variant, variant_id) for variant_id in items}
            if any(not variant for variant in variants.values()):
                raise ValueError("الصنف غير موجود")
            if any(variants[key].stock_qty < qty for key, qty in items.items()):
                raise ValueError("المخزون غير كافٍ")
            sale = Sale(payment_method="cash", buyer_name=buyer_name.strip(), buyer_phone=buyer_phone.strip(), cashier_username=cashier_username.strip() or "admin")
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
            if cash_received < total:
                raise ValueError(f"المبلغ المدفوع أقل من الإجمالي: {money(total)}")
            return sale, cash_received - total


class ReportService:
    @staticmethod
    def low_stock():
        with SessionLocal() as session:
            query = select(Variant).join(Variant.product).where(
                Product.is_active.is_(True),
                Variant.stock_qty <= Variant.reorder_level,
                Variant.reorder_level > 0,
            ).order_by(Variant.stock_qty, Product.name)
            return session.scalars(query).all()

    @staticmethod
    def today():
        start = datetime.combine(datetime.today(), time.min)
        with SessionLocal() as session:
            total = session.scalar(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.created_at >= start, Sale.archived.is_(False)))
            count = session.scalar(select(func.count(Sale.id)).where(Sale.created_at >= start, Sale.archived.is_(False)))
            low = session.scalar(select(func.count(Variant.id)).join(Variant.product).where(Product.is_active.is_(True), Variant.stock_qty <= Variant.reorder_level, Variant.reorder_level > 0))
            return Decimal(str(total or 0)), count or 0, low or 0


def settings() -> dict[str, str]:
    with SessionLocal() as session:
        return {row.key: row.value for row in session.scalars(select(Setting)).all()}


def save_settings(values: dict[str, str]) -> None:
    with SessionLocal.begin() as session:
        for key, value in values.items():
            session.merge(Setting(key=key, value=value.strip()))

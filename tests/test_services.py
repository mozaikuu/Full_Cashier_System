from decimal import Decimal
from app.database import Base, engine
from app.services import CategoryService, ProductService, SaleService


def setup_function():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_sale_reduces_stock_and_records_total():
    CategoryService.save("Drinks")
    category_id = CategoryService.list()[0].id
    ProductService.create("Water", "WAT-1", "123", Decimal("10.50"), Decimal("0"), 5, 1, category_id)
    variant = ProductService.search("123")[0]
    sale = SaleService.checkout({variant.id: 2})
    assert sale.total == Decimal("21.00")
    assert ProductService.search("123")[0].stock_qty == 3

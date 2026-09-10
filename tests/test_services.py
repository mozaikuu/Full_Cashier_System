from decimal import Decimal
from app.database import Base, engine
from app.auth import authenticate, change_password, initialize_auth
from app.services import CategoryService, InventoryService, ProductService, ReportService, SaleService


def setup_function():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def test_sale_reduces_stock_and_records_total():
    CategoryService.save("Drinks")
    category_id = CategoryService.list()[0].id
    ProductService.create("Water", "WAT-1", "123", Decimal("10.50"), Decimal("0"), 5, 1, category_id)
    variant = ProductService.search("123")[0]
    sale, change = SaleService.checkout({variant.id: 2}, Decimal("25.00"))
    assert sale.total == Decimal("21.00")
    assert change == Decimal("4.00")
    assert ProductService.search("123")[0].stock_qty == 3


def test_cash_and_stock_rules_are_enforced():
    CategoryService.save("مشروبات")
    category_id = CategoryService.list()[0].id
    ProductService.create("عصير", "J-1", "456", Decimal("12.00"), Decimal("0"), 1, 1, category_id)
    variant = ProductService.search("456")[0]
    try:
        SaleService.checkout({variant.id: 1}, Decimal("1.00"))
        raise AssertionError("insufficient cash should fail")
    except ValueError:
        pass
    InventoryService.adjust(variant.id, 3, "restock")
    assert ProductService.search("456")[0].stock_qty == 4


def test_product_delete_is_soft_delete():
    CategoryService.save("بقالة")
    category_id = CategoryService.list()[0].id
    ProductService.create("خبز", "B-1", "789", Decimal("8.00"), Decimal("0"), 2, 1, category_id)
    variant = ProductService.search("789")[0]
    ProductService.delete(variant.product_id)
    assert ProductService.search("789") == []


def test_identifiers_generate_and_name_search_works():
    CategoryService.save("حلويات")
    category_id = CategoryService.list()[0].id
    variant = ProductService.create("بسكوت", "", "", Decimal("15.00"), Decimal("0"), 0, 1, category_id)
    assert variant.sku.startswith("PRD-")
    assert variant.barcode.isdigit()
    assert len(variant.barcode) == 8
    assert ProductService.search("بسكوت")[0].barcode == variant.barcode
    assert ProductService.search(variant.barcode)[0].product.name == "بسكوت"


def test_opening_quantity_is_saved():
    CategoryService.save("منظفات")
    category_id = CategoryService.list()[0].id
    variant = ProductService.create("صابون", "", "", Decimal("20.00"), Decimal("0"), 7, 2, category_id)
    assert ProductService.search(variant.barcode)[0].stock_qty == 7


def test_product_edit_updates_quantity():
    CategoryService.save("أدوات")
    category_id = CategoryService.list()[0].id
    variant = ProductService.create("قلم", "", "", Decimal("5.00"), Decimal("0"), 2, 1, category_id)
    ProductService.update(variant.product_id, "قلم أزرق", variant.sku, variant.barcode, Decimal("6.00"), Decimal("0"), 9, 1, [category_id])
    updated = ProductService.search(variant.barcode)[0]
    assert updated.product.name == "قلم أزرق"
    assert updated.stock_qty == 9


def test_reorder_level_can_be_changed():
    CategoryService.save("حدود")
    category_id = CategoryService.list()[0].id
    variant = ProductService.create("ممحاة", "", "", Decimal("2.00"), Decimal("0"), 10, 1, category_id)
    InventoryService.set_reorder_level(variant.id, 6)
    assert ProductService.search(variant.barcode)[0].reorder_level == 6


def test_receipt_delete_does_not_restore_stock():
    CategoryService.save("مخبوزات")
    category_id = CategoryService.list()[0].id
    variant = ProductService.create("عيش", "", "", Decimal("4.00"), Decimal("0"), 5, 1, category_id)
    sale, _ = SaleService.checkout({variant.id: 2}, Decimal("10.00"))
    SaleService.delete_sale(sale.id)
    assert ProductService.search(variant.barcode)[0].stock_qty == 2


def test_admin_can_change_password_with_old_password():
    initialize_auth()
    assert authenticate("1234")
    assert change_password("1234", "5678")
    assert authenticate("5678")


def test_buyer_details_are_saved_on_receipt():
    CategoryService.save("زبائن")
    category_id = CategoryService.list()[0].id
    variant = ProductService.create("كيس", "", "", Decimal("3.00"), Decimal("0"), 2, 1, category_id)
    sale, _ = SaleService.checkout({variant.id: 1}, Decimal("3.00"), "أحمد", "01000000000")
    saved = SaleService.list_sales()[0]
    assert saved.id == sale.id
    assert saved.buyer_name == "أحمد"
    assert saved.buyer_phone == "01000000000"


def test_low_stock_excludes_inactive_products_and_zero_reorder_levels():
    CategoryService.save("اختبار")
    category_id = CategoryService.list()[0].id
    ProductService.create("متوفر", "", "", Decimal("5.00"), Decimal("0"), 10, 2, category_id)
    inactive = ProductService.create("قديم", "", "", Decimal("5.00"), Decimal("0"), 0, 5, category_id)
    ProductService.delete(inactive.product_id)
    ProductService.create("بدون حد", "", "", Decimal("5.00"), Decimal("0"), 0, 0, category_id)
    assert ReportService.today()[2] == 0

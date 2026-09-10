from decimal import Decimal
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QDoubleSpinBox, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QMainWindow, QMessageBox, QPushButton, QSpinBox, QStackedWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)
from sqlalchemy import select
from app.database import SessionLocal
from app.hardware import LabelPrinter, ReceiptPrinter
from app.models import Sale, Setting, Variant
from app.services import CategoryService, InventoryService, ProductService, ReportService, SaleService, money, settings
from app.ui.styles import STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sandy Cashier")
        self.resize(1180, 720)
        self.setStyleSheet(STYLE)
        self.stack = QStackedWidget()
        self.nav = QListWidget()
        self.nav.addItems(["Dashboard", "Checkout", "Products", "Inventory", "Categories", "Sales history", "Settings"])
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        pages = [self.dashboard(), self.checkout(), self.products(), self.inventory(), self.categories(), self.sales(), self.settings_page()]
        for page in pages:
            self.stack.addWidget(page)
        self.nav.setCurrentRow(0)
        shell = QWidget()
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.nav, 1)
        layout.addWidget(self.stack, 5)
        self.setCentralWidget(shell)

    def page(self, title):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        heading = QLabel(title)
        heading.setObjectName("title")
        layout.addWidget(heading)
        return widget, layout

    def dashboard(self):
        widget, layout = self.page("Today at a glance")
        total, count, low = ReportService.today()
        row = QHBoxLayout()
        for label, value in (("Sales today", money(total)), ("Transactions", str(count)), ("Low stock", str(low))):
            metric = QLabel(f"{label}\n{value}")
            metric.setObjectName("metric")
            row.addWidget(metric)
        layout.addLayout(row)
        layout.addStretch()
        return widget

    def checkout(self):
        widget, layout = self.page("Checkout")
        self.scan = QLineEdit()
        self.scan.setPlaceholderText("Scan barcode and press Enter")
        self.scan.returnPressed.connect(self.add_scan)
        layout.addWidget(self.scan)
        self.cart = QTableWidget(0, 4)
        self.cart.setHorizontalHeaderLabels(["Item", "Qty", "Price", "Total"])
        self.cart.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.cart)
        footer = QHBoxLayout()
        self.total_label = QLabel("TOTAL  EGP 0.00")
        self.total_label.setObjectName("title")
        footer.addWidget(self.total_label)
        footer.addStretch()
        pay = QPushButton("Complete cash sale")
        pay.clicked.connect(self.complete_sale)
        footer.addWidget(pay)
        layout.addLayout(footer)
        self.cart_items = {}
        return widget

    def add_scan(self):
        barcode = self.scan.text().strip()
        self.scan.clear()
        matches = ProductService.search(barcode)
        if not matches:
            QMessageBox.warning(self, "Not found", "No active product matches that barcode.")
            return
        variant = matches[0]
        self.cart_items[variant.id] = self.cart_items.get(variant.id, 0) + 1
        self.refresh_cart()

    def refresh_cart(self):
        self.cart.setRowCount(0)
        total = Decimal("0")
        with SessionLocal() as session:
            for variant_id, quantity in self.cart_items.items():
                variant = session.get(Variant, variant_id)
                line_total = Decimal(variant.price) * quantity
                total += line_total
                row = self.cart.rowCount()
                self.cart.insertRow(row)
                values = (variant.product.name, quantity, money(variant.price), money(line_total))
                for column, value in enumerate(values):
                    self.cart.setItem(row, column, QTableWidgetItem(str(value)))
        self.total_label.setText(f"TOTAL  {money(total)}")

    def complete_sale(self):
        if not self.cart_items:
            return
        try:
            sale = SaleService.checkout(self.cart_items)
            ReceiptPrinter().print_sale(sale)
            self.cart_items.clear()
            self.refresh_cart()
            QMessageBox.information(self, "Sale complete", f"Sale #{sale.id} completed.")
        except ValueError as error:
            QMessageBox.warning(self, "Cannot complete sale", str(error))

    def products(self):
        widget, layout = self.page("Products")
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Search name, SKU, or barcode")
        self.product_search.textChanged.connect(self.refresh_products)
        layout.addWidget(self.product_search)
        form = QFormLayout()
        self.p_name, self.p_sku, self.p_barcode = QLineEdit(), QLineEdit(), QLineEdit()
        self.p_price = QDoubleSpinBox(); self.p_price.setMaximum(999999)
        self.p_stock = QSpinBox(); self.p_stock.setMaximum(999999)
        self.p_reorder = QSpinBox(); self.p_reorder.setMaximum(999999)
        self.p_category = QComboBox()
        for label, field in (("Name", self.p_name), ("SKU", self.p_sku), ("Barcode", self.p_barcode), ("Price (EGP)", self.p_price), ("Opening stock", self.p_stock), ("Reorder level", self.p_reorder), ("Category", self.p_category)):
            form.addRow(label, field)
        add = QPushButton("Add product")
        add.clicked.connect(self.add_product)
        form.addRow(add)
        layout.addLayout(form)
        self.product_table = QTableWidget(0, 5)
        self.product_table.setHorizontalHeaderLabels(["Product", "SKU", "Barcode", "Price", "Stock"])
        layout.addWidget(self.product_table)
        self.refresh_product_categories()
        self.refresh_products()
        return widget

    def refresh_product_categories(self):
        self.p_category.clear()
        self.p_category.addItem("Select category", None)
        for category in CategoryService.list():
            self.p_category.addItem(category.name, category.id)

    def add_product(self):
        if not self.p_name.text().strip() or self.p_category.currentData() is None:
            QMessageBox.warning(self, "Missing details", "Name and category are required.")
            return
        try:
            ProductService.create(self.p_name.text(), self.p_sku.text(), self.p_barcode.text(), Decimal(str(self.p_price.value())), Decimal("0"), self.p_stock.value(), self.p_reorder.value(), self.p_category.currentData())
            self.refresh_products()
            QMessageBox.information(self, "Saved", "Product added.")
        except Exception as error:
            QMessageBox.warning(self, "Cannot save", str(error))

    def refresh_products(self):
        if not hasattr(self, "product_table"):
            return
        variants = ProductService.search(self.product_search.text())
        self.product_table.setRowCount(0)
        for variant in variants:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            for column, value in enumerate((variant.product.name, variant.sku, variant.barcode, money(variant.price), variant.stock_qty)):
                self.product_table.setItem(row, column, QTableWidgetItem(str(value)))

    def inventory(self):
        widget, layout = self.page("Inventory")
        self.inventory_table = QTableWidget(0, 4)
        self.inventory_table.setHorizontalHeaderLabels(["Product", "Barcode", "Stock", "Reorder level"])
        layout.addWidget(self.inventory_table)
        controls = QHBoxLayout()
        self.inventory_qty = QSpinBox(); self.inventory_qty.setRange(-999999, 999999)
        restock = QPushButton("Restock / remove"); restock.clicked.connect(lambda: self.adjust_stock("restock"))
        adjust = QPushButton("Set exact stock"); adjust.clicked.connect(lambda: self.adjust_stock("adjustment"))
        controls.addWidget(QLabel("Quantity")); controls.addWidget(self.inventory_qty); controls.addWidget(restock); controls.addWidget(adjust)
        layout.addLayout(controls)
        self.refresh_inventory()
        return widget

    def refresh_inventory(self):
        self.inventory_table.setRowCount(0)
        for variant in ProductService.search():
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            self.inventory_table.setVerticalHeaderItem(row, QTableWidgetItem(str(variant.id)))
            for column, value in enumerate((variant.product.name, variant.barcode, variant.stock_qty, variant.reorder_level)):
                self.inventory_table.setItem(row, column, QTableWidgetItem(str(value)))

    def adjust_stock(self, reason):
        row = self.inventory_table.currentRow()
        if row < 0:
            return
        try:
            variant_id = int(self.inventory_table.verticalHeaderItem(row).text())
            InventoryService.adjust(variant_id, self.inventory_qty.value(), reason)
            self.refresh_inventory()
        except ValueError as error:
            QMessageBox.warning(self, "Cannot update stock", str(error))

    def categories(self):
        widget, layout = self.page("Categories")
        self.category_name = QLineEdit(); self.category_name.setPlaceholderText("Category name")
        add = QPushButton("Add category"); add.clicked.connect(self.add_category)
        layout.addWidget(self.category_name); layout.addWidget(add)
        self.category_table = QTableWidget(0, 2)
        self.category_table.setHorizontalHeaderLabels(["Name", "Sort order"])
        layout.addWidget(self.category_table)
        self.refresh_categories()
        return widget

    def add_category(self):
        if self.category_name.text().strip():
            CategoryService.save(self.category_name.text())
            self.category_name.clear()
            self.refresh_categories()
            self.refresh_product_categories()

    def refresh_categories(self):
        if not hasattr(self, "category_table"):
            return
        self.category_table.setRowCount(0)
        for category in CategoryService.list():
            row = self.category_table.rowCount(); self.category_table.insertRow(row)
            self.category_table.setItem(row, 0, QTableWidgetItem(category.name)); self.category_table.setItem(row, 1, QTableWidgetItem(str(category.sort_order)))

    def sales(self):
        widget, layout = self.page("Sales history")
        layout.addWidget(QLabel("Completed sales are final. Returns and refunds are not available."))
        self.sales_table = QTableWidget(0, 3)
        self.sales_table.setHorizontalHeaderLabels(["Receipt", "Date", "Total"])
        layout.addWidget(self.sales_table)
        self.refresh_sales()
        return widget

    def refresh_sales(self):
        with SessionLocal() as session:
            sales = session.scalars(select(Sale).order_by(Sale.created_at.desc())).all()
        self.sales_table.setRowCount(0)
        for sale in sales:
            row = self.sales_table.rowCount(); self.sales_table.insertRow(row)
            for column, value in enumerate((f"#{sale.id}", sale.created_at.strftime("%Y-%m-%d %H:%M"), money(sale.total))):
                self.sales_table.setItem(row, column, QTableWidgetItem(str(value)))

    def settings_page(self):
        widget, layout = self.page("Settings")
        values = settings(); self.setting_fields = {}
        form = QFormLayout()
        for key in ("store_name", "store_address", "store_phone"):
            field = QLineEdit(values.get(key, "")); self.setting_fields[key] = field
            form.addRow(key.replace("_", " ").title(), field)
        save = QPushButton("Save store details"); save.clicked.connect(self.save_settings)
        test_receipt = QPushButton("Test receipt printer"); test_receipt.clicked.connect(lambda: ReceiptPrinter().print_sale(type("Sale", (), {"lines": [], "total": 0})()))
        test_label = QPushButton("Test label printer"); test_label.clicked.connect(lambda: LabelPrinter().print_label(type("Variant", (), {"product": type("Product", (), {"name": "Test label"})(), "barcode": "000000", "price": 0})()))
        layout.addLayout(form); layout.addWidget(save); layout.addWidget(test_receipt); layout.addWidget(test_label); layout.addStretch()
        return widget

    def save_settings(self):
        with SessionLocal.begin() as session:
            for key, field in self.setting_fields.items():
                session.merge(Setting(key=key, value=field.text().strip()))
        QMessageBox.information(self, "Saved", "Store details updated.")

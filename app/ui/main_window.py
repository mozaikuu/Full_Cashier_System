from decimal import Decimal

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QPainter, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton, QSpinBox,
    QStackedWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView,
)
from sqlalchemy import select

from app.database import SessionLocal
from app.hardware import LabelPrinter, ReceiptPrinter
from app.models import Category, Sale, Setting, Variant
from app.services import CategoryService, InventoryService, ProductService, ReportService, SaleService, money, save_settings, settings
from app.ui.styles import STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("صندوق سَندي")
        self.resize(1200, 760)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(STYLE)
        self.stack = QStackedWidget()
        self.selected_product_id = None
        self.nav = QListWidget()
        self.nav.addItems(["الرئيسية", "البيع", "الأصناف", "المخزون", "الأقسام", "الفواتير", "الإعدادات", "دليل الاستخدام"])
        self.nav.currentRowChanged.connect(self.change_page)
        for page in (self.dashboard(), self.checkout(), self.products(), self.inventory(), self.categories(), self.sales(), self.settings_page(), self.guide()):
            self.stack.addWidget(page)
        self.nav.setCurrentRow(0)
        shell = QWidget()
        layout = QHBoxLayout(shell)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stack, 5)
        layout.addWidget(self.nav, 1)
        self.setCentralWidget(shell)

    def change_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.refresh_dashboard()
        elif index == 1:
            self.scan.setFocus()
        elif index == 2:
            self.refresh_products()
        elif index == 3:
            self.refresh_inventory()
        elif index == 4:
            self.refresh_categories()

    def page(self, title):
        widget, layout = QWidget(), QVBoxLayout()
        widget.setLayout(layout)
        heading = QLabel(title)
        heading.setObjectName("title")
        layout.addWidget(heading)
        return widget, layout

    @staticmethod
    def configure_table(table):
        table.setAlternatingRowColors(True)
        table.setWordWrap(False)
        table.setSortingEnabled(False)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.verticalHeader().setDefaultSectionSize(34)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)

    @staticmethod
    def set_row_number(table, row):
        item = table.item(row, 0)
        if item:
            item.setText(str(row + 1))

    def dashboard(self):
        widget, layout = self.page("ملخص اليوم")
        row = QHBoxLayout()
        self.dashboard_metrics = {}
        for key, label in (("total", "مبيعات اليوم"), ("count", "عدد الفواتير"), ("low", "مخزون منخفض")):
            metric = QLabel()
            metric.setObjectName("metric")
            row.addWidget(metric)
            self.dashboard_metrics[key] = (label, metric)
        layout.addLayout(row)
        quick = QPushButton("فتح شاشة البيع")
        quick.clicked.connect(lambda: self.nav.setCurrentRow(1))
        layout.addWidget(quick)
        layout.addStretch()
        self.refresh_dashboard()
        return widget

    def refresh_dashboard(self):
        if not hasattr(self, "dashboard_metrics"):
            return
        total, count, low = ReportService.today()
        values = {"total": money(total), "count": str(count), "low": str(low)}
        for key, (label, metric) in self.dashboard_metrics.items():
            metric.setText(f"{label}\n{values[key]}")

    def checkout(self):
        widget, layout = self.page("المبيعات")
        self.scan = QLineEdit()
        self.scan.setPlaceholderText("امسح الباركود ثم اضغط Enter")
        self.scan.returnPressed.connect(self.add_scan)
        layout.addWidget(self.scan)
        self.cart = QTableWidget(0, 4)
        self.cart.setHorizontalHeaderLabels(["#", "الصنف", "الكمية", "الإجمالي"])
        self.cart.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.configure_table(self.cart)
        layout.addWidget(self.cart)
        cart_actions = QHBoxLayout()
        remove_item = QPushButton("شيل الصنف المحدد")
        remove_item.clicked.connect(self.remove_cart_item)
        clear_cart = QPushButton("فضّي السلة")
        clear_cart.clicked.connect(self.clear_cart)
        cart_actions.addWidget(remove_item)
        cart_actions.addWidget(clear_cart)
        cart_actions.addStretch()
        layout.addLayout(cart_actions)
        footer = QHBoxLayout()
        self.total_label = QLabel("الإجمالي  EGP 0.00")
        self.total_label.setObjectName("title")
        self.cash = QDoubleSpinBox()
        self.cash.setMaximum(999999999)
        self.cash.setDecimals(2)
        self.cash.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.cash.setSuffix(" جنيه")
        self.cash.valueChanged.connect(self.update_change)
        self.change_label = QLabel("الباقي 0.00 جنيه")
        pay = QPushButton("بيع نقدي")
        pay.clicked.connect(self.complete_sale)
        for item in (self.total_label, QLabel("المبلغ المدفوع"), self.cash, self.change_label, pay):
            footer.addWidget(item)
        layout.addLayout(footer)
        self.cart_items = {}
        return widget

    def remove_cart_item(self):
        row = self.cart.currentRow()
        if row < 0:
            return
        variant_id = list(self.cart_items)[row]
        if self.cart_items[variant_id] > 1:
            self.cart_items[variant_id] -= 1
        else:
            del self.cart_items[variant_id]
        self.refresh_cart()

    def clear_cart(self):
        self.cart_items.clear()
        self.refresh_cart()

    def add_scan(self):
        barcode = self.scan.text().strip()
        self.scan.clear()
        matches = ProductService.search(barcode)
        if not matches:
            QMessageBox.warning(self, "غير موجود", "لا يوجد صنف نشط بهذا الباركود.")
            self.scan.setFocus()
            return
        variant = matches[0]
        self.cart_items[variant.id] = self.cart_items.get(variant.id, 0) + 1
        self.refresh_cart()
        self.scan.setFocus()

    def cart_total(self):
        total = Decimal("0")
        with SessionLocal() as session:
            for variant_id, quantity in self.cart_items.items():
                variant = session.get(Variant, variant_id)
                if variant:
                    total += Decimal(variant.price) * quantity
        return total

    def refresh_cart(self):
        self.cart.setRowCount(0)
        with SessionLocal() as session:
            for variant_id, quantity in self.cart_items.items():
                variant = session.get(Variant, variant_id)
                if not variant:
                    continue
                row = self.cart.rowCount()
                self.cart.insertRow(row)
                line_total = Decimal(variant.price) * quantity
                for column, value in enumerate((str(row + 1), variant.product.name, quantity, money(line_total))):
                    self.cart.setItem(row, column, QTableWidgetItem(str(value)))
        self.total_label.setText(f"الإجمالي  {money(self.cart_total())}")
        self.update_change()

    def update_change(self):
        change = max(Decimal("0"), Decimal(str(self.cash.value())) - self.cart_total())
        self.change_label.setText(f"الباقي {change:,.2f} جنيه")

    def complete_sale(self):
        try:
            sale, change = SaleService.checkout(self.cart_items, Decimal(str(self.cash.value())))
            ReceiptPrinter().print_sale(sale)
            self.cart_items.clear()
            self.cash.setValue(0)
            self.refresh_cart()
            self.refresh_dashboard()
        except ValueError as error:
            QMessageBox.warning(self, "تعذر إتمام البيع", str(error))

    def products(self):
        widget, layout = self.page("المنتجات")
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("دوّر باسم الصنف أو الباركود")
        self.product_search.textChanged.connect(self.refresh_products)
        layout.addWidget(self.product_search)
        form = QFormLayout()
        self.p_name, self.p_sku, self.p_barcode = QLineEdit(), QLineEdit(), QLineEdit()
        self.p_price = QDoubleSpinBox(); self.p_price.setMaximum(999999); self.p_price.setSuffix(" جنيه")
        self.p_cost = QDoubleSpinBox(); self.p_cost.setMaximum(999999); self.p_cost.setSuffix(" جنيه")
        self.p_stock = QSpinBox(); self.p_stock.setMaximum(999999)
        self.p_reorder = QSpinBox(); self.p_reorder.setMaximum(999999)
        self.p_categories = QListWidget(); self.p_categories.setMaximumHeight(90)
        for label, field in (("اسم الصنف", self.p_name), ("الكود الداخلي (اختياري)", self.p_sku), ("الباركود (هيطلع لوحده)", self.p_barcode), ("سعر البيع", self.p_price), ("التكلفة", self.p_cost), ("الكمية الموجودة دلوقتي", self.p_stock), ("نطلب تاني لما يوصل لـ", self.p_reorder), ("الأقسام", self.p_categories)):
            form.addRow(label, field)
        actions = QHBoxLayout()
        for text, callback in (("صنف جديد", self.new_product), ("أضيف صنف", self.add_product), ("عدّل المحدد", self.update_product), ("امسح المحدد", self.delete_product), ("اطبع باركود", self.print_selected_label)):
            button = QPushButton(text); button.clicked.connect(callback); actions.addWidget(button)
        layout.addLayout(form); layout.addLayout(actions)
        self.product_table = QTableWidget(0, 7)
        self.product_table.setHorizontalHeaderLabels(["#", "الصنف", "الكود الداخلي", "الباركود", "السعر", "المخزون", "القسم"])
        self.configure_table(self.product_table)
        self.product_table.itemSelectionChanged.connect(self.load_selected_product)
        layout.addWidget(self.product_table)
        self.refresh_product_categories(); self.refresh_products()
        return widget

    def refresh_product_categories(self):
        self.p_categories.clear()
        for category in CategoryService.list():
            item = QListWidgetItem(category.name, self.p_categories)
            item.setData(Qt.ItemDataRole.UserRole, category.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)

    def selected_category_ids(self):
        return [self.p_categories.item(index).data(Qt.ItemDataRole.UserRole) for index in range(self.p_categories.count()) if self.p_categories.item(index).checkState() == Qt.CheckState.Checked]

    def add_product(self):
        category_ids = self.selected_category_ids()
        if not self.p_name.text().strip() or not category_ids:
            QMessageBox.warning(self, "بيانات ناقصة", "اكتب اسم الصنف واختار قسم واحد على الأقل.")
            return
        try:
            variant = ProductService.create(self.p_name.text(), self.p_sku.text(), self.p_barcode.text(), Decimal(str(self.p_price.value())), Decimal(str(self.p_cost.value())), self.p_stock.value(), self.p_reorder.value(), category_ids[0])
            ProductService.update(variant.product_id, self.p_name.text(), variant.sku, variant.barcode, Decimal(str(self.p_price.value())), Decimal(str(self.p_cost.value())), self.p_stock.value(), self.p_reorder.value(), category_ids)
            self.refresh_products(); self.refresh_inventory(); self.refresh_dashboard(); self.clear_product_form(); QMessageBox.information(self, "تم الحفظ", "تمت إضافة المنتج.")
        except Exception as error:
            QMessageBox.warning(self, "تعذر الحفظ", str(error))

    def selected_variant(self):
        row = self.product_table.currentRow()
        if row < 0 or not self.product_table.item(row, 0): return None
        variant_id = int(self.product_table.item(row, 0).data(Qt.ItemDataRole.UserRole))
        self.selected_product_id = variant_id
        return next((item for item in ProductService.search() if item.id == variant_id), None)

    def load_selected_product(self):
        variant = self.selected_variant()
        if not variant: return
        self.p_name.setText(variant.product.name); self.p_sku.setText(variant.sku or ""); self.p_barcode.setText(variant.barcode or ""); self.p_price.setValue(float(variant.price)); self.p_cost.setValue(float(variant.cost)); self.p_stock.setValue(variant.stock_qty); self.p_reorder.setValue(variant.reorder_level)
        linked = {link.category_id for link in ProductService.categories(variant.product_id)}
        for index in range(self.p_categories.count()): self.p_categories.item(index).setCheckState(Qt.CheckState.Checked if self.p_categories.item(index).data(Qt.ItemDataRole.UserRole) in linked else Qt.CheckState.Unchecked)

    def update_product(self):
        variant = self.selected_variant()
        if not variant: return
        try:
            ProductService.update(variant.product_id, self.p_name.text(), self.p_sku.text(), self.p_barcode.text(), Decimal(str(self.p_price.value())), Decimal(str(self.p_cost.value())), self.p_stock.value(), self.p_reorder.value(), self.selected_category_ids())
            self.refresh_products(); self.refresh_inventory(); self.refresh_dashboard(); QMessageBox.information(self, "تم التحديث", "تم تحديث المنتج.")
        except Exception as error: QMessageBox.warning(self, "تعذر التحديث", str(error))

    def delete_product(self):
        variant = self.selected_variant()
        if not variant or QMessageBox.question(self, "تأكيد الحذف", "هل تريد حذف المنتج المحدد؟") != QMessageBox.StandardButton.Yes: return
        ProductService.delete(variant.product_id); self.refresh_products(); self.refresh_inventory(); self.refresh_dashboard(); self.clear_product_form()

    def print_selected_label(self):
        variant = self.selected_variant()
        if not variant:
            QMessageBox.warning(self, "اختار صنف", "اختار الصنف من الجدول الأول.")
            return
        copies, accepted = QInputDialog.getInt(self, "عدد الباركود", "عايز تطبع كام باركود؟", 1, 1, 999)
        if not accepted:
            return
        LabelPrinter().print_label(variant, copies)
        self.show_barcode_preview(variant.barcode, copies)

    def show_barcode_preview(self, barcode, copies):
        dialog = QDialog(self)
        dialog.setWindowTitle("معاينة الباركود")
        dialog.setModal(False)
        dialog.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout = QVBoxLayout(dialog)
        title = QLabel(f"اتطبع {copies} باركود")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image = QPixmap(520, 180)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        painter.setPen(Qt.GlobalColor.black)
        x = 30
        for index, digit in enumerate(str(barcode)):
            width = 2 + int(digit) % 3
            painter.fillRect(x, 20, width, 105, Qt.GlobalColor.black)
            x += width + (2 if index % 2 else 3)
        painter.setFont(QFont("Arial", 18))
        painter.drawText(30, 155, str(barcode))
        painter.end()
        preview = QLabel()
        preview.setPixmap(image)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(preview)
        dialog.adjustSize()
        self.barcode_preview = dialog
        dialog.show()
        QTimer.singleShot(1000, dialog.close)
        QTimer.singleShot(1100, dialog.deleteLater)

    def new_product(self):
        self.selected_product_id = None
        for field in (self.p_name, self.p_sku, self.p_barcode): field.clear()
        self.p_price.setValue(0); self.p_cost.setValue(0); self.p_stock.setValue(0); self.p_reorder.setValue(0)
        for index in range(self.p_categories.count()): self.p_categories.item(index).setCheckState(Qt.CheckState.Unchecked)
        self.product_table.clearSelection()

    def clear_product_form(self):
        self.new_product()

    def refresh_products(self):
        if not hasattr(self, "product_table"): return
        selected_id = self.selected_product_id
        variants = ProductService.search(self.product_search.text()); self.product_table.setRowCount(0)
        with SessionLocal() as session: categories = {category.id: category.name for category in session.scalars(select(Category)).all()}
        for variant in variants:
            row = self.product_table.rowCount(); self.product_table.insertRow(row)
            names = [categories[link.category_id] for link in ProductService.categories(variant.product_id) if link.category_id in categories]
            values = (str(row + 1), variant.product.name, variant.sku or "", variant.barcode or "", money(variant.price), variant.stock_qty, ", ".join(names))
            for column, value in enumerate(values): self.product_table.setItem(row, column, QTableWidgetItem(str(value)))
            self.product_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, variant.id)
            if variant.id == selected_id:
                self.product_table.selectRow(row)

    def inventory(self):
        widget, layout = self.page("المخزون")
        layout.addWidget(QLabel("اختار صنف. تقدر تغيّر رقم المخزون في الجدول وتضغط Enter، أو استخدم خانة الكمية تحت الجدول."))
        self.inventory_table = QTableWidget(0, 5)
        self.inventory_table.setHorizontalHeaderLabels(["#", "الصنف", "الباركود", "المخزون (اضغط Enter بعد التعديل)", "حد الطلب"])
        self.inventory_table.cellChanged.connect(self.inventory_cell_changed)
        self.configure_table(self.inventory_table)
        layout.addWidget(self.inventory_table)
        controls = QHBoxLayout()
        self.inventory_qty = QSpinBox(); self.inventory_qty.setRange(-999999, 999999)
        restock = QPushButton("زوّد / اخصم من المخزون"); restock.clicked.connect(lambda: self.adjust_stock("restock"))
        adjust = QPushButton("خليها الكمية دي"); adjust.clicked.connect(lambda: self.adjust_stock("adjustment"))
        controls.addWidget(QLabel("الكمية")); controls.addWidget(self.inventory_qty); controls.addWidget(restock); controls.addWidget(adjust)
        layout.addLayout(controls)
        self.refresh_inventory(); return widget

    def refresh_inventory(self):
        self.inventory_table.blockSignals(True)
        self.inventory_table.setRowCount(0)
        for variant in ProductService.search():
            row = self.inventory_table.rowCount(); self.inventory_table.insertRow(row)
            for column, value in enumerate((str(row + 1), variant.product.name, variant.barcode or "", variant.stock_qty, variant.reorder_level)): self.inventory_table.setItem(row, column, QTableWidgetItem(str(value)))
            self.inventory_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, variant.id)
        self.inventory_table.blockSignals(False)

    def inventory_cell_changed(self, row, column):
        if column != 3 or not self.inventory_table.item(row, 0):
            return
        try:
            variant_id = int(self.inventory_table.item(row, 0).data(Qt.ItemDataRole.UserRole))
            quantity = int(self.inventory_table.item(row, column).text())
            InventoryService.adjust(variant_id, quantity, "adjustment")
            self.refresh_inventory()
            self.refresh_products()
            self.refresh_dashboard()
        except (TypeError, ValueError) as error:
            QMessageBox.warning(self, "الكمية مش مظبوطة", "اكتب رقم صحيح للكمية.")
            self.refresh_inventory()

    def adjust_stock(self, reason):
        row = self.inventory_table.currentRow()
        if row < 0: return
        try:
            InventoryService.adjust(int(self.inventory_table.item(row, 0).data(Qt.ItemDataRole.UserRole)), self.inventory_qty.value(), reason)
            self.refresh_inventory()
            self.refresh_products()
            self.refresh_dashboard()
        except ValueError as error: QMessageBox.warning(self, "تعذر تحديث المخزون", str(error))

    def categories(self):
        widget, layout = self.page("التصنيفات")
        layout.addWidget(QLabel("الأقسام بتخلّيك ترتّب الأصناف وتلاقيها بسرعة. اختار قسم من الجدول قبل ما تضيف قسم فرعي."))
        self.category_name = QLineEdit(); self.category_name.setPlaceholderText("اسم التصنيف"); self.subcategory_name = QLineEdit(); self.subcategory_name.setPlaceholderText("اسم التصنيف الفرعي")
        add = QPushButton("إضافة تصنيف"); add.clicked.connect(self.add_category); add_sub = QPushButton("إضافة تصنيف فرعي"); add_sub.clicked.connect(self.add_subcategory); delete = QPushButton("حذف التصنيف المحدد"); delete.clicked.connect(self.delete_category)
        for item in (self.category_name, add, self.subcategory_name, add_sub, delete): layout.addWidget(item)
        self.category_table = QTableWidget(0, 3); self.category_table.setHorizontalHeaderLabels(["#", "القسم", "عدد الأقسام الفرعية"]); self.configure_table(self.category_table); layout.addWidget(self.category_table); self.refresh_categories(); return widget

    def add_category(self):
        if self.category_name.text().strip(): CategoryService.save(self.category_name.text()); self.category_name.clear(); self.refresh_categories(); self.refresh_product_categories()

    def add_subcategory(self):
        row = self.category_table.currentRow()
        if row >= 0 and self.subcategory_name.text().strip(): CategoryService.save_subcategory(int(self.category_table.item(row, 0).data(Qt.ItemDataRole.UserRole)), self.subcategory_name.text()); self.subcategory_name.clear(); self.refresh_categories()

    def delete_category(self):
        row = self.category_table.currentRow()
        if row < 0: return
        try: CategoryService.delete(int(self.category_table.item(row, 0).data(Qt.ItemDataRole.UserRole))); self.refresh_categories(); self.refresh_product_categories()
        except ValueError as error: QMessageBox.warning(self, "تعذر الحذف", str(error))

    def refresh_categories(self):
        if not hasattr(self, "category_table"): return
        self.category_table.setRowCount(0)
        self.category_table.setRowCount(0)
        for category in CategoryService.list():
            row = self.category_table.rowCount(); self.category_table.insertRow(row)
            values = (str(row + 1), category.name, str(len(CategoryService.subcategories(category.id))))
            for column, value in enumerate(values): self.category_table.setItem(row, column, QTableWidgetItem(value))
            self.category_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, category.id)

    def sales(self):
        widget, layout = self.page("الفواتير")
        layout.addWidget(QLabel("هنا هتلاقي كل الفواتير اللي اتباعت. البيع نهائي ومفيش مرتجعات.")); self.sales_table = QTableWidget(0, 3); self.sales_table.setHorizontalHeaderLabels(["الفاتورة", "التاريخ", "الإجمالي"]); layout.addWidget(self.sales_table); self.refresh_sales(); return widget

    def refresh_sales(self):
        with SessionLocal() as session: sales = session.scalars(select(Sale).order_by(Sale.created_at.desc())).all()
        self.sales_table.setRowCount(0)
        for sale in sales:
            row = self.sales_table.rowCount(); self.sales_table.insertRow(row)
            for column, value in enumerate((f"#{sale.id}", sale.created_at.strftime("%Y-%m-%d %H:%M"), money(sale.total))): self.sales_table.setItem(row, column, QTableWidgetItem(str(value)))

    def settings_page(self):
        widget, layout = self.page("الإعدادات")
        layout.addWidget(QLabel("للطباعة: اكتب اسم الطابعة زي ما ظاهر في إعدادات Windows، احفظ، وبعدها دوس اختبار."))
        values = settings(); self.setting_fields = {}; form = QFormLayout()
        for key, label in (("store_name", "اسم المتجر"), ("store_address", "العنوان"), ("store_phone", "الهاتف"), ("receipt_printer", "طابعة الإيصالات"), ("label_printer", "طابعة الملصقات")):
            field = QLineEdit(values.get(key, "")); self.setting_fields[key] = field; form.addRow(label, field)
        save = QPushButton("احفظ الإعدادات"); save.clicked.connect(self.save_settings); receipt = QPushButton("اطبع إيصال تجريبي"); receipt.clicked.connect(self.test_receipt); label = QPushButton("اطبع باركود تجريبي"); label.clicked.connect(self.test_label)
        layout.addLayout(form); layout.addWidget(save); layout.addWidget(receipt); layout.addWidget(label); layout.addStretch(); return widget

    def save_settings(self):
        save_settings({key: field.text() for key, field in self.setting_fields.items()}); QMessageBox.information(self, "تم الحفظ", "تم حفظ إعدادات المتجر.")

    def guide(self):
        widget, layout = self.page("دليل الاستخدام")
        guide = QLabel(
            "<h2>ابدأ هنا</h2>"
            "<p><b>1. الأقسام:</b> اعمل قسم زي مشروبات أو بقالة. اختار القسم من الجدول لو عايز تضيف قسم فرعي.</p>"
            "<p><b>2. الأصناف:</b> اكتب اسم الصنف والسعر والكمية الموجودة واختار قسم. سيب الباركود فاضي وهو هيتعمل أرقام لوحده.</p>"
            "<p><b>3. المخزون:</b> غيّر رقم المخزون في الجدول واضغط Enter، أو اختار صنف واستخدم خانة الكمية تحت الجدول.</p>"
            "<p><b>4. البيع:</b> امسح الباركود واضغط Enter. اكتب المبلغ المدفوع واضغط بيع نقدي.</p>"
            "<p><b>5. طباعة الباركود:</b> من شاشة الأصناف اختار الصنف واضغط اطبع باركود، وبعدها اكتب عدد النسخ.</p>"
            "<p><b>6. الطابعات:</b> من الإعدادات اكتب اسم طابعة Windows واحفظ، وبعدها اطبع اختبار.</p>"
            "<p><b>الدخول:</b> كلمة السر الافتراضية أول مرة هي <b>1234</b>. لو نسيتها استخدم كود الاسترجاع <b>SANDY-RESET</b> من شاشة الدخول وغيّرها.</p>"
            "<p>لو عايز تعدّل صنف: اختاره من الجدول، عدّل البيانات فوق، واضغط عدّل المحدد.</p>"
        )
        guide.setWordWrap(True)
        guide.setTextFormat(Qt.TextFormat.RichText)
        guide.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(guide)
        layout.addStretch()
        return widget

    def test_receipt(self):
        ReceiptPrinter().test()
        QMessageBox.information(self, "اختبار الإيصال", "لو اسم الطابعة متسجل، المفروض يطلع إيصال تجريبي دلوقتي. لو مش متسجل، الاختبار بيتكتب في نافذة التشغيل.")

    def test_label(self):
        LabelPrinter().test()
        QMessageBox.information(self, "اختبار الباركود", "لو اسم طابعة الملصقات متسجل، المفروض يطلع باركود تجريبي دلوقتي. استخدم زر اطبع باركود من شاشة الأصناف لطباعة باركود صنف حقيقي.")
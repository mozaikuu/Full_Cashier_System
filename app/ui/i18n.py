from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QLineEdit, QListWidget, QPushButton, QSpinBox, QDoubleSpinBox, QTableWidget, QWidget

ARABIC = "ar"
ENGLISH = "en"

TRANSLATIONS = {
    "دخول المدير": "Manager Login", "دخول صندوق موسي": "Moussa Cashier Login", "اكتب كلمة السر عشان تفتح البرنامج.": "Enter your password to open the app.",
    "كلمة السر": "Password", "دخول": "Log in", "نسيت كلمة السر؟": "Forgot password?", "كلمة السر غلط": "Incorrect password", "جرّب تاني أو استخدم نسيت كلمة السر.": "Try again or use Forgot password.",
    "استرجاع كلمة السر": "Recover password", "اكتب كود الاسترجاع:": "Enter the recovery code:", "كلمة سر جديدة": "New password", "اكتب كلمة السر الجديدة:": "Enter the new password:",
    "تم التغيير": "Password changed", "كلمة السر اتغيرت. ادخل بالكلمة الجديدة.": "Password changed. Log in with the new password.", "تعذر الاسترجاع": "Recovery failed", "كود الاسترجاع غلط أو كلمة السر قصيرة.": "The recovery code is incorrect or the password is too short.",
    "صندوق سَندي": "Sandy Cashier", "الرئيسية": "Dashboard", "البيع": "Checkout", "الأصناف": "Products", "المخزون": "Inventory", "الأقسام": "Categories", "الفواتير": "Receipts", "الإعدادات": "Settings", "استعراض الأصناف": "Catalog", "دليل الاستخدام": "User guide",
    "ملخص اليوم": "Today's summary", "مبيعات اليوم": "Today's sales", "عدد الفواتير": "Receipt count", "مخزون منخفض": "Low stock", "فتح شاشة البيع": "Open checkout", "الأصناف اللي قربت تخلص": "Items running low", "الصنف": "Product", "الكمية الحالية": "Current quantity", "حد الطلب": "Reorder level",
    "المبيعات": "Checkout", "امسح الباركود ثم اضغط Enter": "Scan the barcode and press Enter", "الكمية": "Quantity", "الإجمالي": "Total", "شيل الصنف المحدد": "Remove selected item", "فضّي السلة": "Clear cart", "جنيه": "EGP", "اكتب المبلغ المدفوع": "Enter amount paid", "الباقي 0.00 جنيه": "Change 0.00 EGP", "بيع نقدي": "Cash sale", "المبلغ المدفوع": "Amount paid", "غير موجود": "Not found", "لا يوجد صنف نشط بهذا الباركود.": "No active product has this barcode.", "تعذر إتمام البيع": "Sale could not be completed",
    "بيانات المشتري (اختياري)": "Buyer details (optional)", "ممكن تسيبه فاضي": "Optional", "اسم المشتري": "Buyer name", "رقم الموبايل": "Phone number", "حفظ ومتابعة": "Save and continue", "تخطي": "Skip",
    "المنتجات": "Products", "دوّر باسم الصنف أو الباركود": "Search by product name or barcode", "باركود الصنف الجاهز": "Existing product barcode", "امسح الباركود هنا واضغط Enter": "Scan the barcode here and press Enter", "استخدم الباركود": "Use barcode", "اختار الأقسام": "Choose categories", "اسم الصنف": "Product name", "الكود الداخلي (اختياري)": "Internal code (optional)", "الباركود (هيطلع لوحده)": "Barcode (generated automatically)", "سعر البيع": "Sale price", "التكلفة": "Cost", "الكمية الموجودة دلوقتي": "Current quantity", "نطلب تاني لما يوصل لـ": "Reorder when it reaches", "الأقسام": "Categories", "صنف جديد": "New product", "أضيف صنف": "Add product", "عدّل المحدد": "Update selected", "امسح المحدد": "Delete selected", "اطبع باركود": "Print barcode", "الكود الداخلي": "Internal code", "السعر": "Price", "القسم": "Category", "اختار قسم أو اكتب اسم الصنف أو الباركود عشان تلاقي الصنف بسرعة.": "Choose a category or search by name or barcode.", "كل الأقسام": "All categories", "بدون قسم": "No category", "بيع الصنف": "Sell product", "الصنف موجود": "Product found", "الباركود ده مرتبط بصنف موجود واتحدد في الجدول.": "This barcode belongs to an existing product and it was selected.",
    "اختيار أقسام الصنف": "Choose product categories", "حفظ الأقسام": "Save categories", "بيانات ناقصة": "Missing information", "اكتب اسم الصنف واختار قسم واحد على الأقل.": "Enter a product name and choose at least one category.", "تم الحفظ": "Saved", "تمت إضافة المنتج.": "Product added.", "تعذر الحفظ": "Could not save", "اختار صنف": "Choose a product", "اختار الصنف من الجدول الأول قبل التعديل.": "Choose a product from the table before updating.", "تم التحديث": "Updated", "تم تحديث المنتج.": "Product updated.", "تعذر التحديث": "Could not update", "تأكيد الحذف": "Confirm deletion", "هل تريد حذف المنتج المحدد؟": "Delete the selected product?", "عدد الباركود": "Barcode quantity", "عايز تطبع كام باركود؟": "How many barcodes should be printed?", "معاينة الباركود": "Barcode preview", "اتطبع ": "Printed ",
    "المخزون": "Inventory", "اختار صنف. تقدر تغيّر رقم المخزون في الجدول وتضغط Enter، أو استخدم خانة الكمية تحت الجدول.": "Choose a product. Edit stock in the table and press Enter, or use the quantity field below.", "الباركود": "Barcode", "المخزون (Enter للتعديل)": "Stock (press Enter to edit)", "حد الطلب (Enter للتعديل)": "Reorder level (press Enter to edit)", "زوّد / اخصم من المخزون": "Add / subtract stock", "خليها الكمية دي": "Set this quantity", "الكمية مش مظبوطة": "Invalid quantity", "اكتب رقم صحيح للكمية.": "Enter a valid quantity.", "تعذر تحديث المخزون": "Could not update inventory",
    "التصنيفات": "Categories", "الأقسام بتخلّيك ترتّب الأصناف وتلاقيها بسرعة. اختار قسم من الجدول قبل ما تضيف قسم فرعي.": "Categories help organize and find products. Select a category before adding a subcategory.", "اسم التصنيف": "Category name", "اسم التصنيف الفرعي": "Subcategory name", "إضافة تصنيف": "Add category", "إضافة تصنيف فرعي": "Add subcategory", "حذف التصنيف المحدد": "Delete selected category", "عدد الأقسام الفرعية": "Subcategory count", "تعذر الحذف": "Could not delete",
    "هنا هتلاقي كل الفواتير. اختار فاتورة عشان تعرضها أو تعدّل كمياتها أو تعيد طباعتها. الحذف بيمسح السجل بس ومش بيرجع فلوس أو مخزون.": "All receipts are here. Select one to view, reprint, or edit its quantities. Deleting only removes the record; it does not refund money or restore stock.", "الفاتورة": "Receipt", "التاريخ": "Date", "المشتري": "Buyer", "رقم الموبايل": "Phone number", "اعرض الفاتورة": "View receipt", "إعادة طباعة": "Reprint", "احذف الفاتورة": "Delete receipt", "تفاصيل الفاتورة": "Receipt details", "حذف الفاتورة": "Delete receipt", "الفاتورة هتتمسح من السجل فقط، ومش هيحصل استرجاع فلوس أو رجوع للمخزون. تكمل؟": "This only deletes the receipt record; no refund or stock restoration will happen. Continue?",
    "للطباعة: اكتب اسم الطابعة زي ما ظاهر في إعدادات Windows، احفظ، وبعدها دوس اختبار.": "For printing, enter the printer name as shown in Windows settings, save, then run a test.", "اسم المتجر": "Store name", "العنوان": "Address", "الهاتف": "Phone", "طابعة الإيصالات": "Receipt printer", "طابعة الملصقات": "Label printer", "احفظ الإعدادات": "Save settings", "اطبع إيصال تجريبي": "Print test receipt", "اطبع باركود تجريبي": "Print test barcode", "غيّر كلمة السر": "Change password", "إرجاع ضبط المصنع": "Factory reset", "اللغة": "Language", "تم حفظ إعدادات المتجر.": "Store settings saved.", "تغيير كلمة السر": "Change password", "كلمة السر القديمة:": "Current password:", "كلمة السر الجديدة:": "New password:", "كلمة السر اتغيرت.": "Password changed.", "كلمة السر القديمة غلط أو الجديدة قصيرة.": "The current password is incorrect or the new one is too short.",
    "اختبار الإيصال": "Receipt test", "اختبار الباركود": "Barcode test", "تحذير خطير": "Critical warning", "تأكيد نهائي": "Final confirmation", "تمت إعادة الضبط": "Reset complete",
    "تعذر إتمام البيع": "Sale could not be completed", "الباركود ده مرتبط بصنف موجود واتحدد في الجدول.": "This barcode belongs to an existing product and it was selected.", "اكتب اسم الصنف واختار قسم واحد على الأقل.": "Enter a product name and choose at least one category.",
    "اختار الصنف من الجدول الأول قبل التعديل.": "Choose a product from the table before updating.", "الكمية مش مظبوطة": "Invalid quantity", "اكتب رقم صحيح للكمية.": "Enter a valid quantity.", "الفاتورة هتتمسح من السجل فقط، ومش هيحصل استرجاع فلوس أو رجوع للمخزون. تكمل؟": "This only deletes the receipt record; no refund or stock restoration will happen. Continue?",
    "كلمة السر القديمة غلط أو الجديدة قصيرة.": "The current password is incorrect or the new one is too short.", "لو اسم الطابعة متسجل، المفروض يطلع إيصال تجريبي دلوقتي. لو مش متسجل، الاختبار بيتكتب في نافذة التشغيل.": "A test receipt should print now if a printer is configured. Otherwise, the test is written to the console.", "لو اسم طابعة الملصقات متسجل، المفروض يطلع باركود تجريبي دلوقتي. استخدم زر اطبع باركود من شاشة الأصناف لطباعة باركود صنف حقيقي.": "A test barcode should print now if a label printer is configured. Use Print barcode on Products for a real product barcode.",
    "ده هيمسح كل الأصناف والفواتير والمخزون نهائياً. تكمل؟": "This permanently deletes all products, receipts, and stock. Continue?", "آخر تأكيد: إرجاع ضبط المصنع؟": "Final confirmation: reset to factory settings?", "البرنامج رجع فاضي. كلمة السر رجعت 1234.": "The app was reset. The password is 1234.", "الفاتورة هتتمسح من السجل فقط، ومش هيحصل استرجاع فلوس أو رجوع للمخزون. تكمل؟": "This only deletes the receipt record; no refund or stock restoration will happen. Continue?",
    "لا يمكن حذف تصنيف مرتبط بمنتجات": "A category linked to products cannot be deleted", "يجب اختيار تصنيف واحد على الأقل": "Choose at least one category", "المنتج غير موجود": "Product not found", "الكمية مينفعش تكون بالسالب": "Quantity cannot be negative", "حد الطلب مينفعش يكون بالسالب": "Reorder level cannot be negative", "الصنف غير موجود": "Product not found", "الفاتورة مش موجودة": "Receipt not found", "سلة المشتريات فارغة": "The cart is empty", "المخزون غير كافٍ": "Insufficient stock", "المبلغ المدفوع أقل من الإجمالي:": "Amount paid is less than the total:",
}

REVERSE_TRANSLATIONS = {english: arabic for arabic, english in TRANSLATIONS.items()}


def language_name(language):
    return "English" if language == ENGLISH else "العربية"


def translate(text, language):
    if not isinstance(text, str):
        return text
    if text.strip() != text:
        leading = text[:len(text) - len(text.lstrip())]
        trailing = text[len(text.rstrip()):]
        return leading + translate(text.strip(), language) + trailing
    mapping = TRANSLATIONS if language == ENGLISH else REVERSE_TRANSLATIONS
    if text in mapping:
        return mapping[text]
    for source, target in mapping.items():
        if text.startswith(source):
            return target + text[len(source):]
    return text


def apply_language(widget, language):
    widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight if language == ENGLISH else Qt.LayoutDirection.RightToLeft)
    if widget.windowTitle():
        widget.setWindowTitle(translate(widget.windowTitle(), language))
    if isinstance(widget, (QLabel, QPushButton)):
        widget.setText(translate(widget.text(), language))
    if isinstance(widget, QLineEdit):
        widget.setPlaceholderText(translate(widget.placeholderText(), language))
    if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
        widget.setSuffix(translate(widget.suffix(), language))
        widget.lineEdit().setPlaceholderText(translate(widget.lineEdit().placeholderText(), language))
    if isinstance(widget, QTableWidget):
        for column in range(widget.columnCount()):
            header = widget.horizontalHeaderItem(column)
            if header:
                header.setText(translate(header.text(), language))
    if isinstance(widget, QComboBox):
        for index in range(widget.count()):
            widget.setItemText(index, translate(widget.itemText(index), language))
    if isinstance(widget, QListWidget):
        for index in range(widget.count()):
            widget.item(index).setText(translate(widget.item(index).text(), language))
    for child in widget.findChildren(QWidget):
        if child.parent() is widget:
            apply_language(child, language)

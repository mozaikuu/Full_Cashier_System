from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.auth import authenticate, reset_password
from app.services import save_settings, settings
from app.ui.i18n import ENGLISH, apply_language, translate
from app.ui.styles import STYLE


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.language = settings().get("language", "ar")
        self.setWindowTitle("دخول المدير")
        self.setModal(True)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(STYLE)
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)
        title = QLabel("دخول صندوق موسي")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addWidget(QLabel("اكتب كلمة السر عشان تفتح البرنامج."))
        form = QFormLayout()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.returnPressed.connect(self.try_login)
        form.addRow("كلمة السر", self.password)
        layout.addLayout(form)
        login = QPushButton("دخول")
        login.clicked.connect(self.try_login)
        forgot = QPushButton("نسيت كلمة السر؟")
        forgot.clicked.connect(self.forgot_password)
        layout.addWidget(login)
        layout.addWidget(forgot)
        self.language_selector = QComboBox()
        self.language_selector.addItem("العربية", "ar")
        self.language_selector.addItem("English", ENGLISH)
        self.language_selector.setCurrentIndex(self.language_selector.findData(self.language))
        self.language_selector.currentIndexChanged.connect(self.change_language)
        layout.addWidget(self.language_selector)
        self.apply_language()

    def change_language(self):
        self.language = self.language_selector.currentData()
        save_settings({"language": self.language})
        self.apply_language()

    def apply_language(self):
        apply_language(self, self.language)

    def try_login(self):
        if authenticate(self.password.text()):
            self.accept()
        else:
            QMessageBox.warning(self, translate("كلمة السر غلط", self.language), translate("جرّب تاني أو استخدم نسيت كلمة السر.", self.language))
            self.password.selectAll()
            self.password.setFocus()

    def forgot_password(self):
        recovery_code, accepted = QInputDialog.getText(self, translate("استرجاع كلمة السر", self.language), translate("اكتب كود الاسترجاع:", self.language))
        if not accepted:
            return
        new_password, accepted = QInputDialog.getText(self, translate("كلمة سر جديدة", self.language), translate("اكتب كلمة السر الجديدة:", self.language), QLineEdit.EchoMode.Password)
        if accepted and reset_password(recovery_code, new_password):
            QMessageBox.information(self, translate("تم التغيير", self.language), translate("كلمة السر اتغيرت. ادخل بالكلمة الجديدة.", self.language))
        else:
            QMessageBox.warning(self, translate("تعذر الاسترجاع", self.language), translate("كود الاسترجاع غلط أو كلمة السر قصيرة.", self.language))
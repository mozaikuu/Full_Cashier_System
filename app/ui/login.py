from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.auth import authenticate_user, reset_password
from app.ui.styles import STYLE


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("دخول الصندوق")
        self.setModal(True)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(STYLE)
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)
        title = QLabel("دخول صندوق سَندي")
        title.setObjectName("title")
        layout.addWidget(title)
        layout.addWidget(QLabel("اكتب اسم المستخدم وكلمة السر."))
        form = QFormLayout()
        self.username = QLineEdit("admin")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.username.returnPressed.connect(self.password.setFocus)
        self.password.returnPressed.connect(self.try_login)
        form.addRow("اسم المستخدم", self.username)
        form.addRow("كلمة السر", self.password)
        layout.addLayout(form)
        login = QPushButton("دخول")
        login.clicked.connect(self.try_login)
        forgot = QPushButton("نسيت كلمة السر؟")
        forgot.clicked.connect(self.forgot_password)
        self.username.textChanged.connect(lambda value: forgot.setVisible(value.strip().lower() == "admin"))
        forgot.setVisible(True)
        layout.addWidget(login)
        layout.addWidget(forgot)

    def try_login(self):
        user = authenticate_user(self.username.text(), self.password.text())
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, "بيانات الدخول غلط", "راجع اسم المستخدم وكلمة السر.")
            self.password.selectAll()
            self.password.setFocus()

    def forgot_password(self):
        recovery_code, accepted = QInputDialog.getText(self, "استرجاع كلمة السر", "اكتب كود الاسترجاع:")
        if not accepted:
            return
        new_password, accepted = QInputDialog.getText(self, "كلمة سر جديدة", "اكتب كلمة السر الجديدة:", QLineEdit.EchoMode.Password)
        if accepted and reset_password(recovery_code, new_password):
            QMessageBox.information(self, "تم التغيير", "كلمة السر اتغيرت. ادخل بالكلمة الجديدة.")
        else:
            QMessageBox.warning(self, "تعذر الاسترجاع", "كود الاسترجاع غلط أو كلمة السر قصيرة.")
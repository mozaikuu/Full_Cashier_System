from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QInputDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from app.auth import authenticate, reset_password
from app.ui.styles import STYLE


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("دخول المدير")
        self.setModal(True)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet(STYLE)
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)
        title = QLabel("دخول صندوق سَندي")
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

    def try_login(self):
        if authenticate(self.password.text()):
            self.accept()
        else:
            QMessageBox.warning(self, "كلمة السر غلط", "جرّب تاني أو استخدم نسيت كلمة السر.")
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
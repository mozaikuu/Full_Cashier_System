from app.database import init_db
from app.auth import initialize_auth
from app.ui.main_window import MainWindow
from app.ui.login import LoginDialog
from PySide6.QtWidgets import QApplication
import sys


def main() -> int:
    init_db()
    initialize_auth()
    application = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec() != LoginDialog.DialogCode.Accepted:
        return 0
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())

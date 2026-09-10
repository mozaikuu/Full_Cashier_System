from app.database import init_db
from app.ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import sys


def main() -> int:
    init_db()
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())

STYLE = """
QWidget { background: #f5f7f8; color: #17252b; font-family: "Segoe UI", "Tahoma"; font-size: 14px; }
QMainWindow { background: #f5f7f8; }
QPushButton { background: #126e70; color: white; border: 0; border-radius: 5px; padding: 11px 16px; min-height: 22px; font-weight: 600; }
QPushButton:hover { background: #0d585a; }
QPushButton#danger { background: #b3261e; }
QPushButton#danger:hover { background: #8f1d18; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background: white; border: 1px solid #c9d5d6; border-radius: 4px; padding: 8px; min-height: 22px; }
QDoubleSpinBox { padding-right: 30px; }
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button { width: 24px; min-height: 14px; subcontrol-origin: border; border-left: 1px solid #c9d5d6; }
QAbstractSpinBox::up-button { subcontrol-position: top right; }
QAbstractSpinBox::down-button { subcontrol-position: bottom right; }
QTableWidget { background: white; border: 1px solid #d7e0e0; gridline-color: #e4ebeb; alternate-background-color: #f3f8f8; }
QTableWidget QTableCornerButton::section { background: #e7eeee; }
QHeaderView::section { background: #e7eeee; padding: 7px; border: 0; font-weight: 600; }
QLabel#title { font-size: 25px; font-weight: 700; color: #123f44; }
QLabel#metric { background: white; border-left: 4px solid #e2a53b; padding: 16px; font-size: 22px; font-weight: 700; }
QListWidget { background: #123f44; color: #d9eeee; border: 0; padding: 8px; }
QListWidget::item { padding: 12px 10px; border-radius: 4px; }
QListWidget::item:selected { background: #e2a53b; color: #17252b; }
"""

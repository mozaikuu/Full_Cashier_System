STYLE = """
QWidget {
    background: #f1f4f3;
    color: #1c2b2e;
    font-family: "Segoe UI", "Tahoma";
    font-size: 14px;
}
QMainWindow { background: #f1f4f3; }
QStackedWidget { background: #f1f4f3; }
QListWidget {
    background: #123f44;
    color: #dceeed;
    border: 0;
    padding: 18px 10px;
    min-width: 176px;
    max-width: 210px;
    outline: 0;
}
QListWidget::item {
    min-height: 30px;
    padding: 12px 14px;
    margin: 3px 0;
    border-radius: 6px;
}
QListWidget::item:hover { background: #1b5559; }
QListWidget::item:selected { background: #e2a53b; color: #17252b; font-weight: 700; }
QLabel#title {
    background: transparent;
    color: #123f44;
    font-size: 28px;
    font-weight: 700;
    padding: 6px 0 14px;
}
QLabel#metric {
    background: #ffffff;
    border: 1px solid #dce5e3;
    border-top: 4px solid #e2a53b;
    border-radius: 8px;
    padding: 18px;
    min-height: 58px;
    font-size: 21px;
    font-weight: 700;
}
QPushButton {
    background: #14777a;
    color: #ffffff;
    border: 0;
    border-radius: 6px;
    padding: 10px 17px;
    min-height: 24px;
    font-weight: 700;
}
QPushButton:hover { background: #0e5d60; }
QPushButton:pressed { background: #094b4e; }
QPushButton:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #e2a53b;
}
QPushButton#danger { background: #b3261e; }
QPushButton#danger:hover { background: #8f1d18; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #ffffff;
    border: 1px solid #c7d5d3;
    border-radius: 6px;
    padding: 9px 10px;
    min-height: 24px;
    selection-background-color: #14777a;
}
QDoubleSpinBox { padding-right: 32px; }
QDoubleSpinBox#paidAmount { padding-right: 10px; }
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
    width: 25px;
    min-height: 14px;
    subcontrol-origin: border;
    border-left: 1px solid #c7d5d3;
}
QAbstractSpinBox::up-button { subcontrol-position: top right; }
QAbstractSpinBox::down-button { subcontrol-position: bottom right; }
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f5f9f8;
    border: 1px solid #d3dfdd;
    border-radius: 6px;
    gridline-color: #e6eeec;
    selection-background-color: #d9eeee;
    selection-color: #143d40;
    outline: 0;
}
QTableWidget::item { padding: 7px; }
QTableWidget QTableCornerButton::section { background: #e8f0ef; border: 0; }
QHeaderView::section {
    background: #e8f0ef;
    color: #214548;
    padding: 10px 8px;
    border: 0;
    border-bottom: 1px solid #d3dfdd;
    font-weight: 700;
}
QFrame#productCard {
    background: #ffffff;
    border: 1px solid #d3dfdd;
    border-radius: 8px;
    padding: 10px;
}
QFrame#productCard:hover { border: 2px solid #14777a; }
QLabel#cardTitle { color: #123f44; font-size: 17px; font-weight: 700; }
QLabel#stockValue { color: #14777a; font-weight: 700; }
QScrollArea { border: 0; background: transparent; }
QMessageBox, QDialog { background: #f1f4f3; }
"""

STYLE = """
QWidget {
    background: #f5f7f6;
    color: #203236;
    font-family: "Segoe UI", "Tahoma";
    font-size: 14px;
}
QMainWindow { background: #f5f7f6; }
QStackedWidget { background: #f5f7f6; }
QListWidget {
    background: #163f43;
    color: #d9e8e6;
    border: 0;
    padding: 22px 12px;
    min-width: 190px;
    max-width: 224px;
    outline: 0;
}
QListWidget::item {
    min-height: 32px;
    padding: 13px 15px;
    margin: 4px 0;
    border-radius: 7px;
}
QListWidget::item:hover { background: #20575a; }
QListWidget::item:selected { background: #e5aa45; color: #193238; font-weight: 700; }
QLabel#title {
    background: transparent;
    color: #163f43;
    font-size: 27px;
    font-weight: 700;
    padding: 8px 0 16px;
}
QLabel#metric {
    background: #ffffff;
    border: 1px solid #dce6e3;
    border-top: 4px solid #e5aa45;
    border-radius: 9px;
    padding: 19px;
    min-height: 62px;
    font-size: 20px;
    font-weight: 700;
}
QPushButton {
    background: #168083;
    color: #ffffff;
    border: 0;
    border-radius: 7px;
    padding: 11px 18px;
    min-height: 25px;
    font-weight: 700;
}
QPushButton:hover { background: #116b6e; }
QPushButton:pressed { background: #0b5558; }
QPushButton:focus {
    background: #116b6e;
    border: 2px solid #e5aa45;
}
QPushButton#danger { background: #b3261e; }
QPushButton#danger:hover { background: #8f1d18; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #ffffff;
    border: 1px solid #c9d8d5;
    border-radius: 7px;
    padding: 9px 10px;
    min-height: 24px;
    selection-background-color: #168083;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 2px solid #e5aa45;
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
    border-radius: 8px;
    gridline-color: #e6eeec;
    selection-background-color: #d7eceb;
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
    border-radius: 9px;
    padding: 12px;
}
QFrame#productCard:hover { border: 2px solid #168083; }
QLabel#cardTitle { color: #163f43; font-size: 17px; font-weight: 700; }
QLabel#stockValue { color: #168083; font-weight: 700; }
QScrollArea { border: 0; background: transparent; }
QMessageBox, QDialog { background: #f5f7f6; }
"""

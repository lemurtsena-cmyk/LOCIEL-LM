MAIN_STYLE = """
QMainWindow,QWidget{background:#1e1e2e;color:#cdd6f4;
    font-family:\'Segoe UI\',Arial,sans-serif;font-size:13px;}
#sidebar{background:#181825;border-right:1px solid #313244;
    min-width:220px;max-width:220px;}
#sidebar QPushButton{background:transparent;color:#cdd6f4;border:none;
    text-align:left;padding:12px 20px;font-size:14px;
    border-radius:8px;margin:2px 8px;}
#sidebar QPushButton:hover{background:#313244;}
#sidebar QPushButton:checked{background:#89b4fa;color:#1e1e2e;font-weight:bold;}
QTableWidget{background:#24273a;border:1px solid #313244;
    border-radius:8px;gridline-color:#313244;
    selection-background-color:#89b4fa;selection-color:#1e1e2e;}
QTableWidget::item{padding:8px;border-bottom:1px solid #313244;}
QHeaderView::section{background:#181825;color:#89b4fa;padding:10px;
    border:none;font-weight:bold;font-size:12px;}
QPushButton{background:#89b4fa;color:#1e1e2e;border:none;
    padding:8px 16px;border-radius:8px;font-weight:bold;font-size:13px;}
QPushButton:hover{background:#74c7ec;}
QPushButton#btn_danger{background:#f38ba8;}
QPushButton#btn_success{background:#a6e3a1;color:#1e1e2e;}
QPushButton#btn_warning{background:#fab387;color:#1e1e2e;}
QPushButton#btn_secondary{background:#313244;color:#cdd6f4;}
QLineEdit,QTextEdit,QComboBox,QSpinBox,QDoubleSpinBox{
    background:#313244;border:1px solid #45475a;border-radius:6px;
    padding:8px 12px;color:#cdd6f4;font-size:13px;}
QLineEdit:focus,QTextEdit:focus,QComboBox:focus,
QSpinBox:focus,QDoubleSpinBox:focus{border:2px solid #89b4fa;}
QComboBox QAbstractItemView{background:#313244;border:1px solid #45475a;
    selection-background-color:#89b4fa;selection-color:#1e1e2e;}
QLabel#title{font-size:22px;font-weight:bold;color:#89b4fa;}
QScrollBar:vertical{background:#1e1e2e;width:8px;border-radius:4px;}
QScrollBar::handle:vertical{background:#45475a;border-radius:4px;}
QScrollBar::handle:vertical:hover{background:#89b4fa;}
QDialog{background:#24273a;}
QTabWidget::pane{border:1px solid #313244;border-radius:8px;}
QTabBar::tab{background:#313244;color:#a6adc8;padding:8px 20px;
    border-radius:6px 6px 0 0;margin-right:2px;}
QTabBar::tab:selected{background:#89b4fa;color:#1e1e2e;font-weight:bold;}
QGroupBox{color:#89b4fa;font-weight:bold;border:1px solid #313244;
    border-radius:8px;margin-top:8px;padding-top:8px;}

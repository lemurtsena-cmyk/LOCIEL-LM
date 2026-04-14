from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui.styles import MAIN_STYLE

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Boutique Pro")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(MAIN_STYLE)
        self._init_ui()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        ml = QHBoxLayout(central)
        ml.setContentsMargins(0,0,0,0)
        ml.setSpacing(0)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        sl = QVBoxLayout(self.sidebar)
        sl.setContentsMargins(0,0,0,0)
        sl.setSpacing(3)

        logo = QFrame()
        logo.setStyleSheet("QFrame{background:#89b4fa;padding:15px;}")
        ll = QVBoxLayout(logo)
        ico = QLabel("🏪")
        ico.setStyleSheet("font-size:34px;")
        ico.setAlignment(Qt.AlignCenter)
        nm = QLabel("Gestion\\nBoutique Pro")
        nm.setStyleSheet("color:#1e1e2e;font-weight:bold;font-size:13px;")
        nm.setAlignment(Qt.AlignCenter)
        ll.addWidget(ico); ll.addWidget(nm)
        sl.addWidget(logo)
        sl.addSpacing(8)

        nav = [("📊","Tableau de Bord",0),("📦","Produits",1),
               ("🛒","Ventes",2),("👥","Clients",3),
               ("🏭","Fournisseurs",4),("💸","Depenses",5),
               ("📈","Rapports",6),("💾","Sauvegarde",7)]

        self._nav_btns = []
        bg = QButtonGroup(self)
        for ico_txt, label, idx in nav:
            btn = QPushButton(f"  {ico_txt}  {label}")
            btn.setCheckable(True)
            bg.addButton(btn)
            btn.clicked.connect(lambda _, i=idx: self._switch(i))
            self._nav_btns.append(btn)
            sl.addWidget(btn)

        sl.addStretch()
        ver = QLabel("v1.0.0  |  Offline")
        ver.setStyleSheet("color:#6c7086;font-size:10px;padding:8px;")
        ver.setAlignment(Qt.AlignCenter)
        sl.addWidget(ver)

        # Stack
        self.stack = QStackedWidget()
        self._load_pages()

        ml.addWidget(self.sidebar)
        ml.addWidget(self.stack)

        self._nav_btns[0].setChecked(True)
        self._switch(0)

    def _load_pages(self):
        from ui.dashboard    import DashboardWidget
        from ui.produits     import ProduitsWidget
        from ui.ventes       import VentesWidget
        from ui.clients      import ClientsWidget
        from ui.fournisseurs import FournisseursWidget
        from ui.depenses     import DepensesWidget
        from ui.rapports     import RapportsWidget
        from ui.sauvegarde   import SauvegardeWidget

        self._pages = [
            DashboardWidget(), ProduitsWidget(), VentesWidget(),
            ClientsWidget(), FournisseursWidget(), DepensesWidget(),
            RapportsWidget(), SauvegardeWidget()
        ]
        for p in self._pages:
            self.stack.addWidget(p)

    def _switch(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._nav_btns):
            btn.setChecked(i == idx)

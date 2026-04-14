from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import database as db

class FournisseursWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(15)
        header = QHBoxLayout()
        title = QLabel("🏭 Gestion des Fournisseurs")
        title.setObjectName("title")
        btn_add = QPushButton("➕ Nouveau Fournisseur")
        btn_add.clicked.connect(self._add)
        header.addWidget(title); header.addStretch(); header.addWidget(btn_add)
        layout.addLayout(header)
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Rechercher...")
        self.search.textChanged.connect(self._filter)
        self.search.setFixedWidth(300)
        layout.addWidget(self.search)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID","Nom","Téléphone","Email","Adresse","Actions"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        for i,w in enumerate([50,200,130,180,200,120]):
            self.table.setColumnWidth(i,w)
        layout.addWidget(self.table)
        self.status = QLabel("")
        layout.addWidget(self.status)

    def _load(self):
        self._all = db.get_all_fournisseurs()
        self._display(self._all)

    def _display(self, fournisseurs):
        self.table.setRowCount(len(fournisseurs))
        for row,f in enumerate(fournisseurs):
            self.table.setItem(row,0,QTableWidgetItem(str(f["id"])))
            self.table.setItem(row,1,QTableWidgetItem(f["nom"]))
            self.table.setItem(row,2,QTableWidgetItem(f["telephone"] or ""))
            self.table.setItem(row,3,QTableWidgetItem(f["email"] or ""))
            self.table.setItem(row,4,QTableWidgetItem(f["adresse"] or ""))
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(4,2,4,2); bl.setSpacing(4)
            be = QPushButton("✏️"); be.setFixedSize(32,28)
            be.clicked.connect(lambda _,fid=f["id"]: self._edit(fid))
            bd = QPushButton("🗑️"); bd.setFixedSize(32,28)
            bd.setObjectName("btn_danger")
            bd.clicked.connect(lambda _,fid=f["id"]: self._delete(fid))
            bl.addWidget(be); bl.addWidget(bd)
            self.table.setCellWidget(row,5,bw)
            self.table.setRowHeight(row,42)

    def _filter(self):
        s = self.search.text().lower()
        self._display([f for f in self._all if s in f["nom"].lower()])

    def _add(self):
        dlg = FournisseurDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._load()

    def _edit(self, fid):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM fournisseurs WHERE id=?",(fid,))
        f = c.fetchone(); conn.close()
        dlg = FournisseurDialog(self, f)
        if dlg.exec_() == QDialog.Accepted:
            self._load()

    def _delete(self, fid):
        if QMessageBox.question(self,"Confirmation",
            "Supprimer ce fournisseur?",
            QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db.delete_fournisseur(fid)
            self._load()

class FournisseurDialog(QDialog):
    def __init__(self, parent=None, fournisseur=None):
        super().__init__(parent)
        self.f = fournisseur
        self.setWindowTitle("Modifier" if fournisseur else "Nouveau Fournisseur")
        self.setFixedSize(420,320)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25,25,25,25)
        layout.setSpacing(12)
        title = QLabel("✏️ Modifier" if fournisseur else "➕ Nouveau Fournisseur")
        title.setObjectName("title")
        layout.addWidget(title)
        form = QFormLayout(); form.setSpacing(10)
        self.inp_nom = QLineEdit()
        form.addRow("Nom: *", self.inp_nom)
        self.inp_tel = QLineEdit()
        form.addRow("Téléphone:", self.inp_tel)
        self.inp_email = QLineEdit()
        form.addRow("Email:", self.inp_email)
        self.inp_adr = QLineEdit()
        form.addRow("Adresse:", self.inp_adr)
        layout.addLayout(form)
        if fournisseur:
            self.inp_nom.setText(fournisseur["nom"])
            self.inp_tel.setText(fournisseur["telephone"] or "")
            self.inp_email.setText(fournisseur["email"] or "")
            self.inp_adr.setText(fournisseur["adresse"] or "")
        btns = QHBoxLayout()
        bc = QPushButton("Annuler"); bc.setObjectName("btn_secondary")
        bc.clicked.connect(self.reject)
        bs = QPushButton("💾 Enregistrer")
        bs.clicked.connect(self._save)
        btns.addWidget(bc); btns.addStretch(); btns.addWidget(bs)
        layout.addLayout(btns)

    def _save(self):
        nom = self.inp_nom.text().strip()
        if not nom:
            QMessageBox.warning(self,"Erreur","Le nom est obligatoire!")
            return
        data = (nom, self.inp_tel.text().strip(),
                self.inp_email.text().strip(), self.inp_adr.text().strip())
        if self.f:
            db.update_fournisseur(self.f["id"], data)
        else:
            db.add_fournisseur(data)
        self.accept()

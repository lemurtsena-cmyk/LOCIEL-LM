from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import database as db
from utils.formatters import format_mga, format_date

class ClientsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(15)

        header = QHBoxLayout()
        title = QLabel("👥 Gestion des Clients")
        title.setObjectName("title")
        btn_add = QPushButton("➕ Nouveau Client")
        btn_add.clicked.connect(self._add)
        header.addWidget(title); header.addStretch()
        header.addWidget(btn_add)
        layout.addLayout(header)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Rechercher un client...")
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
        self._all = db.get_all_clients()
        self._display(self._all)

    def _display(self, clients):
        self.table.setRowCount(len(clients))
        for row,c in enumerate(clients):
            self.table.setItem(row,0,QTableWidgetItem(str(c["id"])))
            self.table.setItem(row,1,QTableWidgetItem(c["nom"]))
            self.table.setItem(row,2,QTableWidgetItem(c["telephone"] or ""))
            self.table.setItem(row,3,QTableWidgetItem(c["email"] or ""))
            self.table.setItem(row,4,QTableWidgetItem(c["adresse"] or ""))
            bw = QWidget(); bl = QHBoxLayout(bw)
            bl.setContentsMargins(4,2,4,2); bl.setSpacing(4)
            be = QPushButton("✏️"); be.setFixedSize(32,28)
            be.clicked.connect(lambda _,cid=c["id"]: self._edit(cid))
            bd = QPushButton("🗑️"); bd.setFixedSize(32,28)
            bd.setObjectName("btn_danger")
            bd.clicked.connect(lambda _,cid=c["id"]: self._delete(cid))
            bl.addWidget(be); bl.addWidget(bd)
            self.table.setCellWidget(row,5,bw)
            self.table.setRowHeight(row,42)

    def _filter(self):
        s = self.search.text().lower()
        self._display([c for c in self._all
            if s in c["nom"].lower() or
            s in (c["telephone"] or "").lower()])

    def _add(self):
        dlg = ClientDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            self._load()
            self._show("✅ Client ajouté!","success")

    def _edit(self, cid):
        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM clients WHERE id=?",(cid,))
        client = c.fetchone(); conn.close()
        dlg = ClientDialog(self, client)
        if dlg.exec_() == QDialog.Accepted:
            self._load()
            self._show("✅ Client modifié!","success")

    def _delete(self, cid):
        if QMessageBox.question(self,"Confirmation",
            "Supprimer ce client?",
            QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db.delete_client(cid)
            self._load()
            self._show("🗑️ Client supprimé","warning")

    def _show(self,msg,typ="info"):
        clrs={"success":"#a6e3a1","error":"#f38ba8",
              "warning":"#fab387","info":"#89b4fa"}
        self.status.setText(msg)
        self.status.setStyleSheet(
            f"color:{clrs.get(typ,\'#cdd6f4\')};font-weight:bold;padding:5px;")
        QTimer.singleShot(4000, lambda: self.status.setText(""))

class ClientDialog(QDialog):
    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.client = client
        self.setWindowTitle("Modifier Client" if client else "Nouveau Client")
        self.setFixedSize(420,320)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25,25,25,25)
        layout.setSpacing(12)
        title = QLabel("✏️ Modifier" if client else "➕ Nouveau Client")
        title.setObjectName("title")
        layout.addWidget(title)
        form = QFormLayout(); form.setSpacing(10)
        self.inp_nom = QLineEdit()
        self.inp_nom.setPlaceholderText("Nom complet")
        form.addRow("Nom: *", self.inp_nom)
        self.inp_tel = QLineEdit()
        self.inp_tel.setPlaceholderText("Ex: 034 00 000 00")
        form.addRow("Téléphone:", self.inp_tel)
        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("email@exemple.com")
        form.addRow("Email:", self.inp_email)
        self.inp_adr = QLineEdit()
        self.inp_adr.setPlaceholderText("Adresse...")
        form.addRow("Adresse:", self.inp_adr)
        layout.addLayout(form)
        if client:
            self.inp_nom.setText(client["nom"])
            self.inp_tel.setText(client["telephone"] or "")
            self.inp_email.setText(client["email"] or "")
            self.inp_adr.setText(client["adresse"] or "")
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
        if self.client:
            db.update_client(self.client["id"], data)
        else:
            db.add_client(data)
        self.accept()

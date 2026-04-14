from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from utils.backup import create_backup, get_backups, restore_backup
from utils.formatters import format_mga

class SauvegardeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30,30,30,30)
        layout.setSpacing(20)

        title = QLabel("💾 Sauvegarde & Restauration")
        title.setObjectName("title")
        layout.addWidget(title)

        info = QLabel(
            "La base de données contient toutes vos données (produits, ventes, clients...)\\n"
            "Effectuez des sauvegardes régulières pour éviter toute perte de données.")
        info.setStyleSheet(
            "background:#24273a;color:#a6adc8;padding:15px;"
            "border-radius:8px;border-left:4px solid #89b4fa;font-size:13px;")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Boutons
        btn_row = QHBoxLayout()
        btn_manual = QPushButton("💾 Sauvegarder Maintenant")
        btn_manual.setObjectName("btn_success")
        btn_manual.clicked.connect(self._backup_now)

        btn_restore = QPushButton("🔄 Restaurer une Sauvegarde")
        btn_restore.setObjectName("btn_warning")
        btn_restore.clicked.connect(self._restore)

        btn_open = QPushButton("📁 Ouvrir Dossier Backup")
        btn_open.setObjectName("btn_secondary")
        btn_open.clicked.connect(self._open_folder)

        btn_row.addWidget(btn_manual)
        btn_row.addWidget(btn_restore)
        btn_row.addWidget(btn_open)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Liste sauvegardes
        lbl = QLabel("📋 Sauvegardes disponibles")
        lbl.setStyleSheet("color:#89b4fa;font-weight:bold;font-size:14px;")
        layout.addWidget(lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Nom du fichier","Date","Taille","Action"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 280)
        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(2, 100)
        layout.addWidget(self.table)

        self.status = QLabel("")
        layout.addWidget(self.status)

    def _load(self):
        backups = get_backups()
        self.table.setRowCount(len(backups))
        for row, b in enumerate(backups):
            self.table.setItem(row, 0, QTableWidgetItem(b["nom"]))
            self.table.setItem(row, 1, QTableWidgetItem(b["date"]))
            size_kb = b["taille"] / 1024
            self.table.setItem(row, 2,
                QTableWidgetItem(f"{size_kb:.1f} Ko"))
            btn = QPushButton("🔄 Restaurer")
            btn.setObjectName("btn_warning")
            btn.clicked.connect(
                lambda _, p=b["chemin"]: self._restore_file(p))
            self.table.setCellWidget(row, 3, btn)
            self.table.setRowHeight(row, 40)

    def _backup_now(self):
        try:
            dest = create_backup(auto=False)
            self._show("✅ Sauvegarde créée: " + dest, "success")
            self._load()
        except Exception as e:
            self._show(f"❌ Erreur: {e}", "error")

    def _restore(self):
        fn, _ = QFileDialog.getOpenFileName(
            self, "Choisir une sauvegarde", "backup",
            "Base de données (*.db)")
        if fn:
            self._restore_file(fn)

    def _restore_file(self, path):
        reply = QMessageBox.warning(
            self, "Confirmation",
            "⚠️ Cette action remplacera TOUTES vos données actuelles!\\n"
            "Voulez-vous continuer?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                restore_backup(path)
                self._show("✅ Restauration réussie! Redémarrez l\'application.", "success")
            except Exception as e:
                self._show(f"❌ Erreur: {e}", "error")

    def _open_folder(self):
        import subprocess, sys, os
        folder = os.environ.get("APP_BACKUP_DIR", "backup")
        os.makedirs(folder, exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", folder])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def _show(self, msg, typ="info"):
        colors = {"success":"#a6e3a1","error":"#f38ba8",
                  "warning":"#fab387","info":"#89b4fa"}
        self.status.setText(msg)
        self.status.setStyleSheet(
            f"color:{colors.get(typ,\'#cdd6f4\')};"
            "font-weight:bold;padding:5px;")
        QTimer.singleShot(5000, lambda: self.status.setText(""))

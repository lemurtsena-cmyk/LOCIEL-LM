import sys
import os

def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

BASE_PATH    = get_base_path()
DB_PATH      = os.path.join(BASE_PATH, "boutique.db")
FACTURES_DIR = os.path.join(BASE_PATH, "factures")
BACKUP_DIR   = os.path.join(BASE_PATH, "backup")

for d in [FACTURES_DIR, BACKUP_DIR]:
    os.makedirs(d, exist_ok=True)

os.environ["APP_DB_PATH"]      = DB_PATH
os.environ["APP_FACTURES_DIR"] = FACTURES_DIR
os.environ["APP_BACKUP_DIR"]   = BACKUP_DIR
os.environ["APP_BASE_PATH"]    = BASE_PATH

import traceback, logging
log_file = os.path.join(BASE_PATH, "error.log")
logging.basicConfig(
    filename=log_file, level=logging.ERROR,
    format="%(asctime)s — %(levelname)s\\n%(message)s\\n",
    datefmt="%Y-%m-%d %H:%M:%S")

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.critical(f"Exception non gérée:\\n{error_msg}")
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        if QApplication.instance():
            QMessageBox.critical(None, "Erreur Critique",
                f"{exc_type.__name__}: {exc_value}\\n\\nDétails: {log_file}")
    except:
        pass

sys.excepthook = handle_exception

def main():
    from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
    from PyQt5.QtGui import (QPixmap, QFont, QPainter, QColor,
                              QLinearGradient, QPen)
    from PyQt5.QtCore import Qt, QTimer

    app = QApplication(sys.argv)
    app.setApplicationName("Gestion Boutique Pro")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Ma Boutique")
    app.setFont(QFont("Segoe UI", 10))

    W, H = 500, 320
    pixmap = QPixmap(W, H)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    grad = QLinearGradient(0, 0, W, H)
    grad.setColorAt(0.0, QColor("#1e1e2e"))
    grad.setColorAt(1.0, QColor("#181825"))
    painter.setBrush(grad)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, W, H, 20, 20)
    painter.setPen(QPen(QColor("#89b4fa"), 2))
    painter.setBrush(Qt.NoBrush)
    painter.drawRoundedRect(1, 1, W-2, H-2, 19, 19)
    painter.setFont(QFont("Segoe UI", 48))
    painter.setPen(QColor("#89b4fa"))
    painter.drawText(0, 20, W, 130, Qt.AlignCenter, "🏪")
    painter.setFont(QFont("Segoe UI", 22, QFont.Bold))
    painter.setPen(QColor("#cdd6f4"))
    painter.drawText(0, 150, W, 45, Qt.AlignCenter, "Gestion Boutique Pro")
    painter.setFont(QFont("Segoe UI", 11))
    painter.setPen(QColor("#89b4fa"))
    painter.drawText(0, 195, W, 30, Qt.AlignCenter, "Mode Offline  •  Ariary (Ar)")
    painter.setBrush(QColor("#313244"))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(50, 245, W-100, 8, 4, 4)
    painter.setBrush(QColor("#89b4fa"))
    painter.drawRoundedRect(50, 245, int((W-100)*0.85), 8, 4, 4)
    painter.setFont(QFont("Segoe UI", 9))
    painter.setPen(QColor("#45475a"))
    painter.drawText(0, 270, W, 30, Qt.AlignCenter, "v1.0.0  —  © 2024 Ma Boutique")
    painter.end()

    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()

    def msg(t):
        splash.showMessage(f"  {t}", Qt.AlignBottom | Qt.AlignLeft, QColor("#89b4fa"))
        app.processEvents()

    msg("Initialisation base de données...")
    try:
        import database as db
        db.DB_PATH = DB_PATH
        db.init_database()
    except Exception as e:
        splash.close()
        QMessageBox.critical(None, "Erreur DB",
            f"Impossible d\'initialiser la base:\\n{e}\\nChemin: {DB_PATH}")
        sys.exit(1)

    msg("Chargement interface...")
    from ui.main_window import MainWindow
    window = MainWindow()
    msg("Démarrage...")
    QTimer.singleShot(2500, splash.close)
    QTimer.singleShot(2500, window.showMaximized)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

import os
import sys
import zipfile
import sqlite3
import tempfile
from datetime import datetime, timedelta

ZIP_NAME = "GestionBoutique_COMPLET.zip"

FILES = {}

# ════════════════════════════════════════════════════════
FILES["main.py"] = '''\
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

# Ajouter le dossier courant au path Python
if BASE_PATH not in sys.path:
    sys.path.insert(0, BASE_PATH)

import traceback
import logging

log_file = os.path.join(BASE_PATH, "error.log")
logging.basicConfig(
    filename=log_file, level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    msg = "".join(traceback.format_exception(
        exc_type, exc_value, exc_traceback))
    logging.critical(msg)
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        if QApplication.instance():
            QMessageBox.critical(None, "Erreur Critique",
                f"{exc_type.__name__}: {exc_value}\\n\\n"
                f"Voir: {log_file}")
    except:
        pass

sys.excepthook = handle_exception

def main():
    from PyQt5.QtWidgets import (QApplication, QSplashScreen,
                                  QMessageBox)
    from PyQt5.QtGui import (QPixmap, QFont, QPainter,
                              QColor, QLinearGradient, QPen)
    from PyQt5.QtCore import Qt, QTimer

    app = QApplication(sys.argv)
    app.setApplicationName("Gestion Boutique Pro")
    app.setApplicationVersion("1.0.0")
    app.setFont(QFont("Segoe UI", 10))

    # Splash
    W, H = 500, 320
    pix = QPixmap(W, H)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    g = QLinearGradient(0, 0, W, H)
    g.setColorAt(0, QColor("#1e1e2e"))
    g.setColorAt(1, QColor("#181825"))
    p.setBrush(g); p.setPen(Qt.NoPen)
    p.drawRoundedRect(0, 0, W, H, 20, 20)
    p.setPen(QPen(QColor("#89b4fa"), 2))
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(1, 1, W-2, H-2, 19, 19)
    p.setFont(QFont("Segoe UI", 48))
    p.setPen(QColor("#89b4fa"))
    p.drawText(0, 20, W, 130, Qt.AlignCenter, "🏪")
    p.setFont(QFont("Segoe UI", 22, QFont.Bold))
    p.setPen(QColor("#cdd6f4"))
    p.drawText(0, 150, W, 45, Qt.AlignCenter, "Gestion Boutique Pro")
    p.setFont(QFont("Segoe UI", 11))
    p.setPen(QColor("#89b4fa"))
    p.drawText(0, 195, W, 30, Qt.AlignCenter,
               "Mode Offline  Ariary (Ar)")
    p.setBrush(QColor("#313244")); p.setPen(Qt.NoPen)
    p.drawRoundedRect(50, 245, W-100, 8, 4, 4)
    p.setBrush(QColor("#89b4fa"))
    p.drawRoundedRect(50, 245, int((W-100)*0.85), 8, 4, 4)
    p.setFont(QFont("Segoe UI", 9))
    p.setPen(QColor("#45475a"))
    p.drawText(0, 270, W, 30, Qt.AlignCenter,
               "v1.0.0  2024 Ma Boutique")
    p.end()

    splash = QSplashScreen(pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlag(Qt.FramelessWindowHint)
    splash.show()

    def msg(t):
        splash.showMessage(
            f"  {t}",
            Qt.AlignBottom | Qt.AlignLeft,
            QColor("#89b4fa"))
        app.processEvents()

    msg("Initialisation base de donnees...")

    try:
        import database as db
        db.DB_PATH = DB_PATH
        db.init_database()
    except Exception as e:
        splash.close()
        QMessageBox.critical(
            None, "Erreur DB",
            f"Impossible d initialiser la base:\\n{e}\\n"
            f"Chemin: {DB_PATH}")
        sys.exit(1)

    msg("Chargement interface...")
    from ui.main_window import MainWindow
    window = MainWindow()

    msg("Demarrage...")
    QTimer.singleShot(2500, splash.close)
    QTimer.singleShot(2500, window.showMaximized)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
'''

# ════════════════════════════════════════════════════════
FILES["database.py"] = '''\
import sqlite3
import os
from datetime import datetime

# Chemin par defaut - sera remplace par main.py
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "boutique.db"
)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_database():
    """Cree les tables si elles n existent pas"""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE,
        description TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS fournisseurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        telephone TEXT, email TEXT, adresse TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS produits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        nom TEXT NOT NULL,
        description TEXT,
        categorie_id INTEGER,
        fournisseur_id INTEGER,
        prix_achat REAL DEFAULT 0,
        prix_vente REAL NOT NULL,
        stock INTEGER DEFAULT 0,
        stock_minimum INTEGER DEFAULT 5,
        unite TEXT DEFAULT "piece",
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (categorie_id) REFERENCES categories(id),
        FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        telephone TEXT, email TEXT, adresse TEXT,
        solde_credit REAL DEFAULT 0,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_facture TEXT UNIQUE,
        client_id INTEGER,
        date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total REAL NOT NULL,
        remise REAL DEFAULT 0,
        montant_paye REAL DEFAULT 0,
        mode_paiement TEXT DEFAULT "especes",
        statut TEXT DEFAULT "payee",
        notes TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS details_ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vente_id INTEGER NOT NULL,
        produit_id INTEGER NOT NULL,
        quantite INTEGER NOT NULL,
        prix_unitaire REAL NOT NULL,
        sous_total REAL NOT NULL,
        FOREIGN KEY (vente_id) REFERENCES ventes(id),
        FOREIGN KEY (produit_id) REFERENCES produits(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS depenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libelle TEXT NOT NULL,
        montant REAL NOT NULL,
        categorie TEXT,
        date_depense TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS parametres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cle TEXT NOT NULL UNIQUE,
        valeur TEXT,
        description TEXT)""")

    # Donnees initiales
    cats = ["General","Alimentation","Boissons","Hygiene",
            "Electromenager","Vetements","Informatique",
            "Papeterie","Telephonie","Autre"]
    for cat in cats:
        c.execute(
            "INSERT OR IGNORE INTO categories (nom) VALUES (?)",
            (cat,))

    params = [
        ("boutique_nom",   "Ma Boutique",  "Nom boutique"),
        ("monnaie",        "Ar",           "Symbole monnaie"),
        ("monnaie_nom",    "Ariary",       "Nom monnaie"),
        ("stock_alerte",   "5",            "Seuil alerte"),
        ("facture_prefix", "FAC",          "Prefixe factures"),
    ]
    for cle, val, desc in params:
        c.execute(
            "INSERT OR IGNORE INTO parametres "
            "(cle,valeur,description) VALUES (?,?,?)",
            (cle, val, desc))

    conn.commit()
    conn.close()

# ── PRODUITS ─────────────────────────────────────────────
def get_all_produits():
    conn = get_connection(); c = conn.cursor()
    c.execute("""
        SELECT p.*, cat.nom as categorie_nom,
               f.nom as fournisseur_nom
        FROM produits p
        LEFT JOIN categories cat ON p.categorie_id=cat.id
        LEFT JOIN fournisseurs f ON p.fournisseur_id=f.id
        ORDER BY p.nom""")
    r = c.fetchall(); conn.close(); return r

def add_produit(data):
    conn = get_connection()
    conn.cursor().execute("""
        INSERT INTO produits
        (code,nom,description,categorie_id,fournisseur_id,
         prix_achat,prix_vente,stock,stock_minimum,unite)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", data)
    conn.commit(); conn.close()

def update_produit(pid, data):
    conn = get_connection()
    conn.cursor().execute("""
        UPDATE produits SET code=?,nom=?,description=?,
        categorie_id=?,fournisseur_id=?,prix_achat=?,
        prix_vente=?,stock=?,stock_minimum=?,unite=?
        WHERE id=?""", (*data, pid))
    conn.commit(); conn.close()

def delete_produit(pid):
    conn = get_connection()
    conn.cursor().execute(
        "DELETE FROM produits WHERE id=?", (pid,))
    conn.commit(); conn.close()

def update_stock(pid, qty, op="soustraction"):
    conn = get_connection()
    sql = ("UPDATE produits SET stock=stock-? WHERE id=?"
           if op == "soustraction"
           else "UPDATE produits SET stock=stock+? WHERE id=?")
    conn.cursor().execute(sql, (qty, pid))
    conn.commit(); conn.close()

# ── VENTES ───────────────────────────────────────────────
def get_all_ventes():
    conn = get_connection(); c = conn.cursor()
    c.execute("""
        SELECT v.*, cl.nom as client_nom
        FROM ventes v
        LEFT JOIN clients cl ON v.client_id=cl.id
        ORDER BY v.date_vente DESC""")
    r = c.fetchall(); conn.close(); return r

def create_vente(vente_data, details):
    conn = get_connection(); c = conn.cursor()
    try:
        num = "FAC-" + datetime.now().strftime("%Y%m%d%H%M%S")
        c.execute("""
            INSERT INTO ventes
            (numero_facture,client_id,total,remise,
             montant_paye,mode_paiement,statut,notes)
            VALUES (?,?,?,?,?,?,?,?)""", (num, *vente_data))
        vid = c.lastrowid
        for d in details:
            c.execute("""
                INSERT INTO details_ventes
                (vente_id,produit_id,quantite,
                 prix_unitaire,sous_total)
                VALUES (?,?,?,?,?)""", (vid, *d))
            c.execute(
                "UPDATE produits SET stock=stock-? WHERE id=?",
                (d[1], d[0]))
        conn.commit()
        return vid, num
    except Exception as e:
        conn.rollback(); raise e
    finally:
        conn.close()

def get_details_vente(vid):
    conn = get_connection(); c = conn.cursor()
    c.execute("""
        SELECT dv.*, p.nom as produit_nom,
               p.code as produit_code
        FROM details_ventes dv
        JOIN produits p ON dv.produit_id=p.id
        WHERE dv.vente_id=?""", (vid,))
    r = c.fetchall(); conn.close(); return r

# ── CLIENTS ──────────────────────────────────────────────
def get_all_clients():
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT * FROM clients ORDER BY nom")
    r = c.fetchall(); conn.close(); return r

def add_client(data):
    conn = get_connection()
    conn.cursor().execute(
        "INSERT INTO clients "
        "(nom,telephone,email,adresse) VALUES (?,?,?,?)",
        data)
    conn.commit(); conn.close()

def update_client(cid, data):
    conn = get_connection()
    conn.cursor().execute(
        "UPDATE clients SET nom=?,telephone=?,"
        "email=?,adresse=? WHERE id=?",
        (*data, cid))
    conn.commit(); conn.close()

def delete_client(cid):
    conn = get_connection()
    conn.cursor().execute(
        "DELETE FROM clients WHERE id=?", (cid,))
    conn.commit(); conn.close()

# ── FOURNISSEURS ─────────────────────────────────────────
def get_all_fournisseurs():
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT * FROM fournisseurs ORDER BY nom")
    r = c.fetchall(); conn.close(); return r

def add_fournisseur(data):
    conn = get_connection()
    conn.cursor().execute(
        "INSERT INTO fournisseurs "
        "(nom,telephone,email,adresse) VALUES (?,?,?,?)",
        data)
    conn.commit(); conn.close()

def update_fournisseur(fid, data):
    conn = get_connection()
    conn.cursor().execute(
        "UPDATE fournisseurs SET nom=?,telephone=?,"
        "email=?,adresse=? WHERE id=?",
        (*data, fid))
    conn.commit(); conn.close()

def delete_fournisseur(fid):
    conn = get_connection()
    conn.cursor().execute(
        "DELETE FROM fournisseurs WHERE id=?", (fid,))
    conn.commit(); conn.close()

# ── CATEGORIES ───────────────────────────────────────────
def get_all_categories():
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT * FROM categories ORDER BY nom")
    r = c.fetchall(); conn.close(); return r

def add_categorie(nom, desc=""):
    conn = get_connection()
    conn.cursor().execute(
        "INSERT INTO categories (nom,description) VALUES (?,?)",
        (nom, desc))
    conn.commit(); conn.close()

# ── DEPENSES ─────────────────────────────────────────────
def get_all_depenses(d1=None, d2=None, cat=None):
    conn = get_connection(); c = conn.cursor()
    q = "SELECT * FROM depenses WHERE 1=1"; p = []
    if d1: q += " AND DATE(date_depense)>=?"; p.append(d1)
    if d2: q += " AND DATE(date_depense)<=?"; p.append(d2)
    if cat and cat != "Toutes":
        q += " AND categorie=?"; p.append(cat)
    q += " ORDER BY date_depense DESC"
    c.execute(q, p); r = c.fetchall(); conn.close(); return r

def add_depense(libelle, montant, categorie, date_dep, notes=""):
    conn = get_connection()
    conn.cursor().execute(
        "INSERT INTO depenses "
        "(libelle,montant,categorie,date_depense,notes) "
        "VALUES (?,?,?,?,?)",
        (libelle, montant, categorie, date_dep, notes))
    conn.commit(); conn.close()

def update_depense(did, libelle, montant,
                   categorie, date_dep, notes=""):
    conn = get_connection()
    conn.cursor().execute(
        "UPDATE depenses SET libelle=?,montant=?,"
        "categorie=?,date_depense=?,notes=? WHERE id=?",
        (libelle, montant, categorie, date_dep, notes, did))
    conn.commit(); conn.close()

def delete_depense(did):
    conn = get_connection()
    conn.cursor().execute(
        "DELETE FROM depenses WHERE id=?", (did,))
    conn.commit(); conn.close()

# ── STATISTIQUES DASHBOARD ───────────────────────────────
def get_stats_dashboard():
    conn = get_connection(); c = conn.cursor()
    stats = {}
    c.execute("""SELECT COALESCE(SUM(total),0) as total,
        COUNT(*) as nombre FROM ventes
        WHERE DATE(date_vente)=DATE('now')""")
    r = c.fetchone()
    stats["ventes_jour"] = {
        "total": r["total"], "nombre": r["nombre"]}
    c.execute("""SELECT COALESCE(SUM(total),0) as total,
        COUNT(*) as nombre FROM ventes
        WHERE strftime('%Y-%m',date_vente)=
              strftime('%Y-%m','now')""")
    r = c.fetchone()
    stats["ventes_mois"] = {
        "total": r["total"], "nombre": r["nombre"]}
    c.execute("""SELECT COUNT(*) as n FROM produits
        WHERE stock<=stock_minimum""")
    stats["stock_critique"] = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) as n FROM produits")
    stats["total_produits"] = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) as n FROM clients")
    stats["total_clients"] = c.fetchone()["n"]
    c.execute("""SELECT COALESCE(SUM(
        dv.sous_total-(p.prix_achat*dv.quantite)),0) as b
        FROM details_ventes dv
        JOIN produits p ON dv.produit_id=p.id
        JOIN ventes v ON dv.vente_id=v.id
        WHERE strftime('%Y-%m',v.date_vente)=
              strftime('%Y-%m','now')""")
    stats["benefice_mois"] = c.fetchone()["b"]
    c.execute("""SELECT COALESCE(SUM(montant),0) as t
        FROM depenses
        WHERE strftime('%Y-%m',date_depense)=
              strftime('%Y-%m','now')""")
    stats["depenses_mois"] = c.fetchone()["t"]
    conn.close(); return stats

def get_ventes_par_jour(nb=7):
    conn = get_connection(); c = conn.cursor()
    c.execute("""SELECT DATE(date_vente) as jour,
        SUM(total) as total, COUNT(*) as nombre
        FROM ventes
        WHERE date_vente>=DATE('now',?)
        GROUP BY DATE(date_vente)
        ORDER BY jour""", (f"-{nb} days",))
    r = c.fetchall(); conn.close(); return r

def get_top_produits(limit=10):
    conn = get_connection(); c = conn.cursor()
    c.execute("""SELECT p.nom,
        SUM(dv.quantite) as total_vendu,
        SUM(dv.sous_total) as chiffre_affaires
        FROM details_ventes dv
        JOIN produits p ON dv.produit_id=p.id
        GROUP BY p.id,p.nom
        ORDER BY total_vendu DESC LIMIT ?""", (limit,))
    r = c.fetchall(); conn.close(); return r

# ── RAPPORTS ─────────────────────────────────────────────
def get_rapport_ventes(d1=None, d2=None):
    conn = get_connection(); c = conn.cursor()
    w = "WHERE 1=1"; p = []
    if d1: w += " AND DATE(v.date_vente)>=?"; p.append(d1)
    if d2: w += " AND DATE(v.date_vente)<=?"; p.append(d2)
    c.execute(f"""SELECT COUNT(*) as nb_ventes,
        COALESCE(SUM(total),0) as chiffre_affaires,
        COALESCE(SUM(remise),0) as total_remises,
        COALESCE(SUM(montant_paye),0) as total_encaisse,
        COALESCE(AVG(total),0) as panier_moyen
        FROM ventes v {w}""", p)
    resume = dict(c.fetchone())
    c.execute(f"""SELECT DATE(v.date_vente) as jour,
        COUNT(*) as nb_ventes,
        SUM(v.total) as total,
        SUM(v.montant_paye) as encaisse
        FROM ventes v {w}
        GROUP BY DATE(v.date_vente)
        ORDER BY jour""", p)
    par_jour = c.fetchall()
    c.execute(f"""SELECT mode_paiement,
        COUNT(*) as nombre, SUM(total) as total
        FROM ventes v {w}
        GROUP BY mode_paiement
        ORDER BY total DESC""", p)
    par_paiement = c.fetchall()
    c.execute(f"""SELECT cl.nom as client_nom,
        COUNT(v.id) as nb_achats,
        SUM(v.total) as total_achats
        FROM ventes v
        JOIN clients cl ON v.client_id=cl.id {w}
        GROUP BY cl.id,cl.nom
        ORDER BY total_achats DESC LIMIT 10""", p)
    top_clients = c.fetchall()
    c.execute(f"""SELECT COALESCE(SUM(
        dv.sous_total-(p.prix_achat*dv.quantite)),0) as b
        FROM details_ventes dv
        JOIN produits p ON dv.produit_id=p.id
        JOIN ventes v ON dv.vente_id=v.id {w}""", p)
    benefice = c.fetchone()["b"]
    conn.close()
    return {"resume": resume, "par_jour": par_jour,
            "par_paiement": par_paiement,
            "top_clients": top_clients,
            "benefice_brut": benefice}

def get_rapport_produits(d1=None, d2=None):
    conn = get_connection(); c = conn.cursor()
    p = []; df = ""
    if d1: df += " AND DATE(v.date_vente)>=?"; p.append(d1)
    if d2: df += " AND DATE(v.date_vente)<=?"; p.append(d2)
    c.execute(f"""SELECT p.code,p.nom,p.prix_achat,
        p.prix_vente,p.stock,p.unite,
        cat.nom as categorie,
        COALESCE(SUM(dv.quantite),0) as qte_vendue,
        COALESCE(SUM(dv.sous_total),0) as ca,
        COALESCE(SUM(dv.sous_total-
            (p.prix_achat*dv.quantite)),0) as benefice
        FROM produits p
        LEFT JOIN details_ventes dv ON p.id=dv.produit_id
        LEFT JOIN ventes v ON dv.vente_id=v.id
            {("AND 1=1"+df) if df else ""}
        LEFT JOIN categories cat ON p.categorie_id=cat.id
        GROUP BY p.id ORDER BY qte_vendue DESC""", p)
    produits = c.fetchall()
    c.execute("""SELECT
        COALESCE(SUM(stock*prix_achat),0) as valeur_achat,
        COALESCE(SUM(stock*prix_vente),0) as valeur_vente,
        COUNT(*) as total_produits,
        SUM(CASE WHEN stock<=0 THEN 1 ELSE 0 END) as en_rupture,
        SUM(CASE WHEN stock<=stock_minimum AND stock>0
            THEN 1 ELSE 0 END) as critique
        FROM produits""")
    stock_stats = dict(c.fetchone())
    c.execute("""SELECT cat.nom as categorie,
        COUNT(p.id) as nb_produits,
        COALESCE(SUM(dv.quantite),0) as qte_vendue,
        COALESCE(SUM(dv.sous_total),0) as ca
        FROM categories cat
        LEFT JOIN produits p ON p.categorie_id=cat.id
        LEFT JOIN details_ventes dv ON p.id=dv.produit_id
        LEFT JOIN ventes v ON dv.vente_id=v.id
        GROUP BY cat.id,cat.nom ORDER BY ca DESC""")
    par_cat = c.fetchall()
    conn.close()
    return {"produits": produits,
            "stock_stats": stock_stats,
            "par_categorie": par_cat}

def get_rapport_financier(d1=None, d2=None):
    conn = get_connection(); c = conn.cursor()
    wv = "WHERE 1=1"; wd = "WHERE 1=1"
    pv = []; pd_ = []
    if d1:
        wv += " AND DATE(date_vente)>=?"; pv.append(d1)
        wd += " AND DATE(date_depense)>=?"; pd_.append(d1)
    if d2:
        wv += " AND DATE(date_vente)<=?"; pv.append(d2)
        wd += " AND DATE(date_depense)<=?"; pd_.append(d2)
    c.execute(
        f"SELECT COALESCE(SUM(total),0) as t FROM ventes {wv}",
        pv)
    ca = c.fetchone()["t"]
    c.execute(
        f"SELECT COALESCE(SUM(montant_paye),0) as t "
        f"FROM ventes {wv}", pv)
    recettes = c.fetchone()["t"]
    c.execute(
        f"SELECT COALESCE(SUM(montant),0) as t "
        f"FROM depenses {wd}", pd_)
    depenses = c.fetchone()["t"]
    c.execute(f"""SELECT COALESCE(SUM(
        p.prix_achat*dv.quantite),0) as cout
        FROM details_ventes dv
        JOIN produits p ON dv.produit_id=p.id
        JOIN ventes v ON dv.vente_id=v.id {wv}""", pv)
    cout = c.fetchone()["cout"]
    c.execute(f"""SELECT
        strftime('%Y-%m',date_vente) as mois,
        SUM(total) as ca,
        SUM(montant_paye) as encaisse
        FROM ventes {wv}
        GROUP BY mois ORDER BY mois""", pv)
    ca_mensuel = c.fetchall()
    c.execute(f"""SELECT
        strftime('%Y-%m',date_depense) as mois,
        SUM(montant) as total
        FROM depenses {wd}
        GROUP BY mois ORDER BY mois""", pd_)
    dep_mensuel = c.fetchall()
    conn.close()
    ben_brut = ca - cout
    ben_net  = ben_brut - depenses
    marge    = (ben_brut/ca*100) if ca > 0 else 0
    return {"ca": ca, "recettes": recettes,
            "depenses": depenses,
            "cout_marchandises": cout,
            "benefice_brut": ben_brut,
            "benefice_net": ben_net,
            "marge_brute": marge,
            "ca_mensuel": ca_mensuel,
            "depenses_mensuel": dep_mensuel}

def get_stats_depenses(d1=None, d2=None):
    conn = get_connection(); c = conn.cursor()
    w = "WHERE 1=1"; p = []
    if d1: w += " AND DATE(date_depense)>=?"; p.append(d1)
    if d2: w += " AND DATE(date_depense)<=?"; p.append(d2)
    c.execute(f"""SELECT categorie,
        SUM(montant) as total, COUNT(*) as nombre
        FROM depenses {w}
        GROUP BY categorie ORDER BY total DESC""", p)
    par_cat = c.fetchall()
    c.execute(
        f"SELECT COALESCE(SUM(montant),0) as t "
        f"FROM depenses {w}", p)
    total = c.fetchone()["t"]
    c.execute(f"""SELECT
        strftime('%Y-%m',date_depense) as mois,
        SUM(montant) as total, COUNT(*) as nombre
        FROM depenses {w}
        GROUP BY mois ORDER BY mois""", p)
    par_mois = c.fetchall()
    conn.close()
    return {"total": total,
            "par_categorie": par_cat,
            "par_mois": par_mois}
'''

# ════════════════════════════════════════════════════════
FILES["utils/__init__.py"] = ""

FILES["utils/formatters.py"] = '''\
def format_mga(montant, show_symbol=True):
    try:
        montant = float(montant or 0)
        sign = "-" if montant < 0 else ""
        fmt = f"{abs(montant):,.0f}".replace(",", " ")
        return f"{sign}{fmt} Ar" if show_symbol else f"{sign}{fmt}"
    except:
        return "0 Ar"

def format_pourcentage(v):
    try: return f"{float(v):.1f}%"
    except: return "0.0%"

def format_date(date_str, fmt="%d/%m/%Y"):
    from datetime import datetime
    try:
        s = str(date_str)[:19]
        for f in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
            try: return datetime.strptime(s,f).strftime(fmt)
            except: continue
        return s[:10]
    except: return str(date_str)[:10]
'''

FILES["utils/backup.py"] = '''\
import os, shutil
from datetime import datetime
import database as db

BACKUP_DIR = os.environ.get("APP_BACKUP_DIR", "backup")

def create_backup(auto=False):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    prefix = "auto" if auto else "manuel"
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(
        BACKUP_DIR, f"boutique_{prefix}_{now}.db")
    shutil.copy2(db.DB_PATH, dest)
    _cleanup(10)
    return dest

def _cleanup(max_keep=10):
    files = sorted([
        os.path.join(BACKUP_DIR, f)
        for f in os.listdir(BACKUP_DIR)
        if f.endswith(".db")
    ], key=os.path.getmtime)
    while len(files) > max_keep:
        os.remove(files.pop(0))

def get_backups():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    files = []
    for f in os.listdir(BACKUP_DIR):
        if f.endswith(".db"):
            path = os.path.join(BACKUP_DIR, f)
            files.append({
                "nom": f, "chemin": path,
                "taille": os.path.getsize(path),
                "date": datetime.fromtimestamp(
                    os.path.getmtime(path)
                ).strftime("%d/%m/%Y %H:%M")})
    return sorted(files,
                  key=lambda x: x["date"], reverse=True)

def restore_backup(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Introuvable: {path}")
    shutil.copy2(path, db.DB_PATH)
'''

FILES["utils/pdf_generator.py"] = '''\
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable)
from utils.formatters import format_mga

FACTURES_DIR = os.environ.get("APP_FACTURES_DIR", "factures")
os.makedirs(FACTURES_DIR, exist_ok=True)

def generer_facture(vente, details):
    num = vente["numero_facture"] or f"FAC-{vente[\'id\']}"
    filename = os.path.join(FACTURES_DIR, f"{num}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm)

    primary = colors.HexColor("#2563eb")
    light   = colors.HexColor("#f3f4f6")
    green   = colors.HexColor("#16a34a")

    def sty(name, **kw):
        return ParagraphStyle(
            name, fontName="Helvetica",
            fontSize=10, **kw)

    story = []
    hd = [[
        Paragraph("GESTION BOUTIQUE PRO",
            sty("t", fontSize=20,
                textColor=primary,
                fontName="Helvetica-Bold")),
        Paragraph(
            f"<b>FACTURE</b><br/>"
            f"<font color=\'#2563eb\' size=\'14\'>"
            f"{num}</font>",
            sty("r", alignment=TA_RIGHT,
                fontName="Helvetica-Bold",
                fontSize=12))
    ]]
    ht = Table(hd, colWidths=[10*cm, 7*cm])
    ht.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(ht)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=primary, spaceAfter=0.5*cm))

    date_str = (str(vente["date_vente"])[:16]
                if vente["date_vente"]
                else datetime.now().strftime("%d/%m/%Y %H:%M"))
    client_nom = (vente.get("client_nom")
                  or "Client de passage")
    client_tel = vente.get("client_tel") or "-"

    info = [[
        Paragraph(
            f"<b>DATE:</b> {date_str}<br/>"
            f"<b>PAIEMENT:</b> "
            f"{vente.get(\'mode_paiement\',\'especes\').upper()}"
            f"<br/><b>STATUT:</b> "
            f"{vente.get(\'statut\',\'\').upper()}",
            sty("i", leading=18)),
        Paragraph(
            f"<b>CLIENT:</b> {client_nom}<br/>"
            f"<b>TEL:</b> {client_tel}",
            sty("ir", leading=18, alignment=TA_RIGHT))
    ]]
    it = Table(info, colWidths=[9*cm, 8*cm])
    it.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), light),
        ("ROWPADDING",(0,0),(-1,-1), 10)]))
    story.append(it)
    story.append(Spacer(1, 0.5*cm))

    td = [["#","Code","Designation",
           "Qte","Prix Unit.","Sous-Total"]]
    for i, d in enumerate(details, 1):
        td.append([
            str(i),
            d.get("produit_code") or "-",
            d.get("produit_nom",""),
            str(d["quantite"]),
            format_mga(d["prix_unitaire"]),
            format_mga(d["sous_total"])])

    dt = Table(td,
        colWidths=[1*cm,2.5*cm,6*cm,
                   1.5*cm,3*cm,3*cm])
    dt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), primary),
        ("TEXTCOLOR",(0,0),(-1,0), colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1), 10),
        ("ROWPADDING",(0,0),(-1,-1), 8),
        ("ALIGN",(3,1),(-1,-1),"RIGHT"),
        ("GRID",(0,0),(-1,-1), 0.5,
         colors.HexColor("#d1d5db")),
        *[("BACKGROUND",(0,i),(-1,i), light)
          for i in range(2,len(td),2)],
        ("FONTNAME",(5,1),(5,-1),"Helvetica-Bold"),
        ("TEXTCOLOR",(5,1),(5,-1), green),
    ]))
    story.append(dt)
    story.append(Spacer(1, 0.5*cm))

    total  = vente.get("total", 0)
    remise = vente.get("remise", 0)
    paye   = vente.get("montant_paye", 0)
    reste  = total - paye

    rows = []
    rows.append(["Sous-Total:",
                 format_mga(total + remise)])
    if remise > 0:
        rows.append(["Remise:",
                     f"-{format_mga(remise)}"])
    rows.append(["TOTAL TTC:", format_mga(total)])
    rows.append(["Paye:", format_mga(paye)])
    if reste > 0:
        rows.append(["Reste a Payer:",
                     format_mga(reste)])
    elif paye > total:
        rows.append(["Monnaie Rendue:",
                     format_mga(paye - total)])

    tt = Table(rows,
               colWidths=[6*cm, 4*cm],
               hAlign="RIGHT")
    tt.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"RIGHT"),
        ("FONTSIZE",(0,0),(-1,-1), 10),
        ("ROWPADDING",(0,0),(-1,-1), 6),
        ("FONTNAME",(0,-3),(-1,-3),"Helvetica-Bold"),
        ("FONTSIZE",(0,-3),(-1,-3), 13),
        ("TEXTCOLOR",(1,-3),(1,-3), green),
        ("BACKGROUND",(0,-3),(-1,-3),
         colors.HexColor("#f0fdf4")),
        ("LINEABOVE",(0,-3),(-1,-3), 2, primary),
    ]))
    story.append(tt)
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=colors.HexColor("#d1d5db")))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Merci pour votre confiance !",
        sty("f", fontSize=9,
            textColor=colors.HexColor("#9ca3af"),
            alignment=TA_CENTER)))
    doc.build(story)
    return filename
'''

# ════════════════════════════════════════════════════════
#  FONCTION CREATION DB
# ════════════════════════════════════════════════════════
def create_boutique_db():
    """Crée boutique.db avec toutes les tables et données"""
    tmp = tempfile.NamedTemporaryFile(
        suffix=".db", delete=False)
    tmp_path = tmp.name
    tmp.close()

    conn = sqlite3.connect(tmp_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Tables
    c.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL UNIQUE,
        description TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

    CREATE TABLE IF NOT EXISTS fournisseurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        telephone TEXT, email TEXT, adresse TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

    CREATE TABLE IF NOT EXISTS produits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        nom TEXT NOT NULL,
        description TEXT,
        categorie_id INTEGER,
        fournisseur_id INTEGER,
        prix_achat REAL DEFAULT 0,
        prix_vente REAL NOT NULL,
        stock INTEGER DEFAULT 0,
        stock_minimum INTEGER DEFAULT 5,
        unite TEXT DEFAULT 'piece',
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (categorie_id) REFERENCES categories(id),
        FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id));

    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        telephone TEXT, email TEXT, adresse TEXT,
        solde_credit REAL DEFAULT 0,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

    CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_facture TEXT UNIQUE,
        client_id INTEGER,
        date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total REAL NOT NULL,
        remise REAL DEFAULT 0,
        montant_paye REAL DEFAULT 0,
        mode_paiement TEXT DEFAULT 'especes',
        statut TEXT DEFAULT 'payee',
        notes TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id));

    CREATE TABLE IF NOT EXISTS details_ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vente_id INTEGER NOT NULL,
        produit_id INTEGER NOT NULL,
        quantite INTEGER NOT NULL,
        prix_unitaire REAL NOT NULL,
        sous_total REAL NOT NULL,
        FOREIGN KEY (vente_id) REFERENCES ventes(id),
        FOREIGN KEY (produit_id) REFERENCES produits(id));

    CREATE TABLE IF NOT EXISTS depenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libelle TEXT NOT NULL,
        montant REAL NOT NULL,
        categorie TEXT,
        date_depense TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT);

    CREATE TABLE IF NOT EXISTS parametres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cle TEXT NOT NULL UNIQUE,
        valeur TEXT,
        description TEXT);
    """)

    # Catégories
    for cat in ["General","Alimentation","Boissons",
                "Hygiene","Electromenager","Vetements",
                "Informatique","Papeterie",
                "Telephonie","Autre"]:
        c.execute(
            "INSERT OR IGNORE INTO categories (nom) VALUES (?)",
            (cat,))

    # Fournisseur
    c.execute("""INSERT OR IGNORE INTO fournisseurs
        (nom,telephone,adresse) VALUES (?,?,?)""",
        ("Fournisseur General",
         "000 00 000 00", "Madagascar"))

    # Paramètres
    for cle, val, desc in [
        ("boutique_nom",  "Ma Boutique", "Nom"),
        ("monnaie",       "Ar",          "Symbole"),
        ("monnaie_nom",   "Ariary",      "Nom monnaie"),
        ("stock_alerte",  "5",           "Seuil"),
        ("facture_prefix","FAC",         "Prefixe"),
        ("version_db",    "1.0.0",       "Version"),
    ]:
        c.execute("""INSERT OR IGNORE INTO parametres
            (cle,valeur,description) VALUES (?,?,?)""",
            (cle, val, desc))

    # Produits demo
    today = datetime.now()
    for code,nom,cat_id,pa,pv,stock,smin,unite in [
        ("P001","Riz 5kg",         2,8000, 12000,50,10,"sac"),
        ("P002","Huile 1L",        2,4500,  7000,30, 5,"litre"),
        ("P003","Sucre 1kg",       2,2500,  4000,40, 8,"kg"),
        ("P004","Farine 1kg",      2,2000,  3500,25, 5,"kg"),
        ("P005","Savon",           4,1200,  2000,60,10,"piece"),
        ("P006","Eau 1.5L",        3,800,   1500,100,20,"piece"),
        ("P007","Coca-Cola 33cl",  3,1000,  1800,80,15,"piece"),
        ("P008","Cahier 100p",     8,1500,  2500,45,10,"piece"),
        ("P009","Stylo Bic",       8,300,    600,200,30,"piece"),
        ("P010","Lait concentre",  2,2200,  3500,35, 8,"boite"),
    ]:
        c.execute("""INSERT OR IGNORE INTO produits
            (code,nom,categorie_id,fournisseur_id,
             prix_achat,prix_vente,stock,
             stock_minimum,unite)
            VALUES (?,?,?,1,?,?,?,?,?)""",
            (code,nom,cat_id,pa,pv,stock,smin,unite))

    # Clients demo
    for nom,tel,email,adr in [
        ("Rakoto Jean",   "034 12 345 67",
         "rakoto@email.mg",  "Antananarivo"),
        ("Rabe Marie",    "033 98 765 43",
         "rabe@email.mg",    "Fianarantsoa"),
        ("Randria Paul",  "032 11 222 33",
         "",                  "Toamasina"),
        ("Rasoa Nathalie","034 55 666 77",
         "rasoa@email.mg",   "Mahajanga"),
    ]:
        c.execute("""INSERT OR IGNORE INTO clients
            (nom,telephone,email,adresse)
            VALUES (?,?,?,?)""",
            (nom,tel,email,adr))

    # Dépenses demo
    for lib,mont,cat,jours,notes in [
        ("Loyer mensuel",    150000,"Loyer",       5,""),
        ("Facture electricite",45000,"Electricite",10,""),
        ("Facture eau",       12000,"Eau",         12,""),
        ("Salaire employe",  200000,"Salaires",     1,""),
        ("Transport",         25000,"Transport",    3,""),
        ("Internet/Tel",      15000,"Internet/Telephone",8,""),
    ]:
        date_ = (today - timedelta(days=jours)
                 ).strftime("%Y-%m-%d")
        c.execute("""INSERT INTO depenses
            (libelle,montant,categorie,
             date_depense,notes)
            VALUES (?,?,?,?,?)""",
            (lib,mont,cat,date_,notes))

    conn.commit()
    conn.close()

    with open(tmp_path, "rb") as f:
        data = f.read()
    os.unlink(tmp_path)
    return data


# ════════════════════════════════════════════════════════
#  CREATION DU ZIP
# ════════════════════════════════════════════════════════
def create_zip():
    print("\n  Création du ZIP — Gestion Boutique Pro")
    print("  " + "="*42)

    print("  Generation boutique.db...")
    db_bytes = create_boutique_db()
    print(f"  OK boutique.db ({len(db_bytes)//1024} Ko)")

    DIRS = ["ui/","utils/","assets/","factures/","backup/"]

    with zipfile.ZipFile(
            ZIP_NAME, "w",
            zipfile.ZIP_DEFLATED,
            compresslevel=9) as zf:

        for d in DIRS:
            zf.mkdir(f"GestionBoutique/{d}")
            print(f"  Dossier: {d}")

        # boutique.db
        zf.writestr(
            "GestionBoutique/boutique.db", db_bytes)
        print(f"  OK boutique.db (base de donnees)")

        # Tous les fichiers
        for path, content in FILES.items():
            arc = f"GestionBoutique/{path}"
            zf.writestr(arc, content.encode("utf-8"))
            size = len(content.encode("utf-8"))
            print(f"  OK {path} ({size} octets)")

    sz = os.path.getsize(ZIP_NAME) / 1024
    print(f"""
  {'='*42}
  ZIP cree    : {ZIP_NAME}
  Taille      : {sz:.1f} Ko
  Fichiers    : {len(FILES)+1}
  {'='*42}
""")


if __name__ == "__main__":
    create_zip()

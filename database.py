import sqlite3
import os
from datetime import datetime

DB_PATH = os.environ.get("APP_DB_PATH", "boutique.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_database():
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
        code TEXT UNIQUE, nom TEXT NOT NULL, description TEXT,
        categorie_id INTEGER, fournisseur_id INTEGER,
        prix_achat REAL DEFAULT 0, prix_vente REAL NOT NULL,
        stock INTEGER DEFAULT 0, stock_minimum INTEGER DEFAULT 5,
        unite TEXT DEFAULT "piece",
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (categorie_id) REFERENCES categories(id),
        FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL, telephone TEXT, email TEXT, adresse TEXT,
        solde_credit REAL DEFAULT 0,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    c.execute("""CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_facture TEXT UNIQUE, client_id INTEGER,
        date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total REAL NOT NULL, remise REAL DEFAULT 0,
        montant_paye REAL DEFAULT 0,
        mode_paiement TEXT DEFAULT "especes",
        statut TEXT DEFAULT "payee", notes TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS details_ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vente_id INTEGER NOT NULL, produit_id INTEGER NOT NULL,
        quantite INTEGER NOT NULL, prix_unitaire REAL NOT NULL,
        sous_total REAL NOT NULL,
        FOREIGN KEY (vente_id) REFERENCES ventes(id),
        FOREIGN KEY (produit_id) REFERENCES produits(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS depenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libelle TEXT NOT NULL, montant REAL NOT NULL,
        categorie TEXT, date_depense TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT)""")

    c.execute("INSERT OR IGNORE INTO categories (nom) VALUES (\'General\')")
    conn.commit()
    conn.close()

# ── PRODUITS ──
def get_all_produits():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT p.*, cat.nom as categorie_nom, f.nom as fournisseur_nom
        FROM produits p
        LEFT JOIN categories cat ON p.categorie_id = cat.id
        LEFT JOIN fournisseurs f ON p.fournisseur_id = f.id
        ORDER BY p.nom""")
    r = c.fetchall(); conn.close(); return r

def add_produit(data):
    conn = get_connection()
    conn.cursor().execute("""INSERT INTO produits
        (code,nom,description,categorie_id,fournisseur_id,
         prix_achat,prix_vente,stock,stock_minimum,unite)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", data)
    conn.commit(); conn.close()

def update_produit(pid, data):
    conn = get_connection()
    conn.cursor().execute("""UPDATE produits SET code=?,nom=?,description=?,
        categorie_id=?,fournisseur_id=?,prix_achat=?,prix_vente=?,
        stock=?,stock_minimum=?,unite=? WHERE id=?""", (*data, pid))
    conn.commit(); conn.close()

def delete_produit(pid):
    conn = get_connection()
    conn.cursor().execute("DELETE FROM produits WHERE id=?", (pid,))
    conn.commit(); conn.close()

def update_stock(pid, qty, op="soustraction"):
    conn = get_connection()
    sql = ("UPDATE produits SET stock=stock-? WHERE id=?" if op=="soustraction"
           else "UPDATE produits SET stock=stock+? WHERE id=?")
    conn.cursor().execute(sql, (qty, pid))
    conn.commit(); conn.close()

# ── VENTES ──
def get_all_ventes():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT v.*, cl.nom as client_nom FROM ventes v
        LEFT JOIN clients cl ON v.client_id=cl.id
        ORDER BY v.date_vente DESC""")
    r = c.fetchall(); conn.close(); return r

def create_vente(vente_data, details):
    conn = get_connection()
    c = conn.cursor()
    try:
        num = f"FAC-{datetime.now().strftime(\'%Y%m%d%H%M%S\')}"
        c.execute("""INSERT INTO ventes
            (numero_facture,client_id,total,remise,montant_paye,
             mode_paiement,statut,notes)
            VALUES (?,?,?,?,?,?,?,?)""", (num, *vente_data))
        vid = c.lastrowid
        for d in details:
            c.execute("""INSERT INTO details_ventes
                (vente_id,produit_id,quantite,prix_unitaire,sous_total)
                VALUES (?,?,?,?,?)""", (vid, *d))
            c.execute("UPDATE produits SET stock=stock-? WHERE id=?",
                      (d[1], d[0]))
        conn.commit()
        return vid, num
    except Exception as e:
        conn.rollback(); raise e
    finally:
        conn.close()

def get_details_vente(vid):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT dv.*, p.nom as produit_nom, p.code as produit_code
        FROM details_ventes dv JOIN produits p ON dv.produit_id=p.id
        WHERE dv.vente_id=?""", (vid,))
    r = c.fetchall(); conn.close(); return r

# ── CLIENTS ──
def get_all_clients():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM clients ORDER BY nom")
    r = c.fetchall(); conn.close(); return r

def add_client(data):
    conn = get_connection()
    conn.cursor().execute(
        "INSERT INTO clients (nom,telephone,email,adresse) VALUES (?,?,?,?)", data)
    conn.commit(); conn.close()

def update_client(cid, data):
    conn = get_connection()
    conn.cursor().execute(
        "UPDATE clients SET nom=?,telephone=?,email=?,adresse=? WHERE id=?",
        (*data, cid))
    conn.commit(); conn.close()

def delete_client(cid):
    conn = get_connection()
    conn.cursor().execute("DELETE FROM clients WHERE id=?", (cid,))
    conn.commit(); conn.close()

# ── FOURNISSEURS ──
def get_all_fournisseurs():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM fournisseurs ORDER BY nom")
    r = c.fetchall(); conn.close(); return r

def add_fournisseur(data):
    conn = get_connection()
    conn.cursor().execute(
        "INSERT INTO fournisseurs (nom,telephone,email,adresse) VALUES (?,?,?,?)", data)
    conn.commit(); conn.close()

def update_fournisseur(fid, data):
    conn = get_connection()
    conn.cursor().execute(
        "UPDATE fournisseurs SET nom=?,telephone=?,email=?,adresse=? WHERE id=?",
        (*data, fid))
    conn.commit(); conn.close()

def delete_fournisseur(fid):
    conn = get_connection()
    conn.cursor().execute("DELETE FROM fournisseurs WHERE id=?", (fid,))
    conn.commit(); conn.close()

# ── CATEGORIES ──
def get_all_categories():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM categories ORDER BY nom")
    r = c.fetchall(); conn.close(); return r

def add_categorie(nom, desc=""):
    conn = get_connection()
    conn.cursor().execute(
        "INSERT INTO categories (nom,description) VALUES (?,?)", (nom, desc))
    conn.commit(); conn.close()

# ── DEPENSES ──
def get_all_depenses(d1=None, d2=None, cat=None):
    conn = get_connection()
    c = conn.cursor()
    q = "SELECT * FROM depenses WHERE 1=1"
    p = []
    if d1: q += " AND DATE(date_depense)>=?"; p.append(d1)
    if d2: q += " AND DATE(date_depense)<=?"; p.append(d2)
    if cat and cat != "Toutes": q += " AND categorie=?"; p.append(cat)
    q += " ORDER BY date_depense DESC"
    c.execute(q, p)
    r = c.fetchall(); conn.close(); return r

def add_depense(libelle, montant, categorie, date_dep, notes=""):
    conn = get_connection()
    conn.cursor().execute(
        "INSERT INTO depenses (libelle,montant,categorie,date_depense,notes) VALUES (?,?,?,?,?)",
        (libelle, montant, categorie, date_dep, notes))
    conn.commit(); conn.close()

def update_depense(did, libelle, montant, categorie, date_dep, notes=""):
    conn = get_connection()
    conn.cursor().execute(
        "UPDATE depenses SET libelle=?,montant=?,categorie=?,date_depense=?,notes=? WHERE id=?",
        (libelle, montant, categorie, date_dep, notes, did))
    conn.commit(); conn.close()

def delete_depense(did):
    conn = get_connection()
    conn.cursor().execute("DELETE FROM depenses WHERE id=?", (did,))
    conn.commit(); conn.close()

# ── STATS DASHBOARD ──
def get_stats_dashboard():
    conn = get_connection()
    c = conn.cursor()
    stats = {}
    c.execute("""SELECT COALESCE(SUM(total),0) as total, COUNT(*) as nombre
        FROM ventes WHERE DATE(date_vente)=DATE(\'now\')""")
    r = c.fetchone()
    stats["ventes_jour"] = {"total": r["total"], "nombre": r["nombre"]}
    c.execute("""SELECT COALESCE(SUM(total),0) as total, COUNT(*) as nombre
        FROM ventes WHERE strftime(\'%Y-%m\',date_vente)=strftime(\'%Y-%m\',\'now\')""")
    r = c.fetchone()
    stats["ventes_mois"] = {"total": r["total"], "nombre": r["nombre"]}
    c.execute("SELECT COUNT(*) as n FROM produits WHERE stock<=stock_minimum")
    stats["stock_critique"] = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) as n FROM produits")
    stats["total_produits"] = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) as n FROM clients")
    stats["total_clients"] = c.fetchone()["n"]
    c.execute("""SELECT COALESCE(SUM(dv.sous_total-(p.prix_achat*dv.quantite)),0) as b
        FROM details_ventes dv JOIN produits p ON dv.produit_id=p.id
        JOIN ventes v ON dv.vente_id=v.id
        WHERE strftime(\'%Y-%m\',v.date_vente)=strftime(\'%Y-%m\',\'now\')""")
    stats["benefice_mois"] = c.fetchone()["b"]
    c.execute("""SELECT COALESCE(SUM(montant),0) as t FROM depenses
        WHERE strftime(\'%Y-%m\',date_depense)=strftime(\'%Y-%m\',\'now\')""")
    stats["depenses_mois"] = c.fetchone()["t"]
    conn.close()
    return stats

def get_ventes_par_jour(nb=7):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT DATE(date_vente) as jour,
        SUM(total) as total, COUNT(*) as nombre
        FROM ventes WHERE date_vente>=DATE(\'now\',?)
        GROUP BY DATE(date_vente) ORDER BY jour""", (f"-{nb} days",))
    r = c.fetchall(); conn.close(); return r

def get_top_produits(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT p.nom, SUM(dv.quantite) as total_vendu,
        SUM(dv.sous_total) as chiffre_affaires
        FROM details_ventes dv JOIN produits p ON dv.produit_id=p.id
        GROUP BY p.id,p.nom ORDER BY total_vendu DESC LIMIT ?""", (limit,))
    r = c.fetchall(); conn.close(); return r

# ── RAPPORTS ──
def get_rapport_ventes(d1=None, d2=None):
    conn = get_connection()
    c = conn.cursor()
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
        COUNT(*) as nb_ventes, SUM(v.total) as total,
        SUM(v.montant_paye) as encaisse
        FROM ventes v {w} GROUP BY DATE(v.date_vente) ORDER BY jour""", p)
    par_jour = c.fetchall()
    c.execute(f"""SELECT mode_paiement, COUNT(*) as nombre, SUM(total) as total
        FROM ventes v {w} GROUP BY mode_paiement ORDER BY total DESC""", p)
    par_paiement = c.fetchall()
    c.execute(f"""SELECT cl.nom as client_nom,
        COUNT(v.id) as nb_achats, SUM(v.total) as total_achats
        FROM ventes v JOIN clients cl ON v.client_id=cl.id {w}
        GROUP BY cl.id,cl.nom ORDER BY total_achats DESC LIMIT 10""", p)
    top_clients = c.fetchall()
    c.execute(f"""SELECT COALESCE(SUM(dv.sous_total-(p.prix_achat*dv.quantite)),0) as b
        FROM details_ventes dv JOIN produits p ON dv.produit_id=p.id
        JOIN ventes v ON dv.vente_id=v.id {w}""", p)
    benefice = c.fetchone()["b"]
    conn.close()
    return {"resume": resume, "par_jour": par_jour,
            "par_paiement": par_paiement,
            "top_clients": top_clients, "benefice_brut": benefice}

def get_rapport_produits(d1=None, d2=None):
    conn = get_connection()
    c = conn.cursor()
    p = []
    if d1: p.append(d1)
    if d2: p.append(d2)
    date_filter = ""
    if d1: date_filter += " AND DATE(v.date_vente)>=?"
    if d2: date_filter += " AND DATE(v.date_vente)<=?"
    c.execute(f"""SELECT p.code,p.nom,p.prix_achat,p.prix_vente,p.stock,
        p.unite, cat.nom as categorie,
        COALESCE(SUM(dv.quantite),0) as qte_vendue,
        COALESCE(SUM(dv.sous_total),0) as ca,
        COALESCE(SUM(dv.sous_total-(p.prix_achat*dv.quantite)),0) as benefice
        FROM produits p
        LEFT JOIN details_ventes dv ON p.id=dv.produit_id
        LEFT JOIN ventes v ON dv.vente_id=v.id {("AND 1=1"+date_filter) if date_filter else ""}
        LEFT JOIN categories cat ON p.categorie_id=cat.id
        GROUP BY p.id ORDER BY qte_vendue DESC""", p)
    produits = c.fetchall()
    c.execute("""SELECT
        COALESCE(SUM(stock*prix_achat),0) as valeur_achat,
        COALESCE(SUM(stock*prix_vente),0) as valeur_vente,
        COUNT(*) as total_produits,
        SUM(CASE WHEN stock<=0 THEN 1 ELSE 0 END) as en_rupture,
        SUM(CASE WHEN stock<=stock_minimum AND stock>0 THEN 1 ELSE 0 END) as critique
        FROM produits""")
    stock_stats = dict(c.fetchone())
    c.execute(f"""SELECT cat.nom as categorie,
        COUNT(p.id) as nb_produits,
        COALESCE(SUM(dv.quantite),0) as qte_vendue,
        COALESCE(SUM(dv.sous_total),0) as ca
        FROM categories cat
        LEFT JOIN produits p ON p.categorie_id=cat.id
        LEFT JOIN details_ventes dv ON p.id=dv.produit_id
        LEFT JOIN ventes v ON dv.vente_id=v.id
        GROUP BY cat.id,cat.nom ORDER BY ca DESC""")
    par_categorie = c.fetchall()
    conn.close()
    return {"produits": produits, "stock_stats": stock_stats,
            "par_categorie": par_categorie}

def get_rapport_financier(d1=None, d2=None):
    conn = get_connection()
    c = conn.cursor()
    wv = "WHERE 1=1"; wd = "WHERE 1=1"; pv = []; pd_ = []
    if d1: wv += " AND DATE(date_vente)>=?"; pv.append(d1)
          wd += " AND DATE(date_depense)>=?"; pd_.append(d1)
    if d2: wv += " AND DATE(date_vente)<=?"; pv.append(d2)
          wd += " AND DATE(date_depense)<=?"; pd_.append(d2)
    c.execute(f"SELECT COALESCE(SUM(total),0) as t FROM ventes {wv}", pv)
    ca = c.fetchone()["t"]
    c.execute(f"SELECT COALESCE(SUM(montant_paye),0) as t FROM ventes {wv}", pv)
    recettes = c.fetchone()["t"]
    c.execute(f"SELECT COALESCE(SUM(montant),0) as t FROM depenses {wd}", pd_)
    depenses = c.fetchone()["t"]
    c.execute(f"""SELECT COALESCE(SUM(p.prix_achat*dv.quantite),0) as cout
        FROM details_ventes dv JOIN produits p ON dv.produit_id=p.id
        JOIN ventes v ON dv.vente_id=v.id {wv}""", pv)
    cout = c.fetchone()["cout"]
    c.execute(f"""SELECT strftime(\'%Y-%m\',date_vente) as mois,
        SUM(total) as ca, SUM(montant_paye) as encaisse
        FROM ventes {wv} GROUP BY mois ORDER BY mois""", pv)
    ca_mensuel = c.fetchall()
    c.execute(f"""SELECT strftime(\'%Y-%m\',date_depense) as mois,
        SUM(montant) as total FROM depenses {wd}
        GROUP BY mois ORDER BY mois""", pd_)
    dep_mensuel = c.fetchall()
    conn.close()
    ben_brut = ca - cout
    ben_net  = ben_brut - depenses
    marge    = (ben_brut / ca * 100) if ca > 0 else 0
    return {"ca": ca, "recettes": recettes, "depenses": depenses,
            "cout_marchandises": cout, "benefice_brut": ben_brut,
            "benefice_net": ben_net, "marge_brute": marge,
            "ca_mensuel": ca_mensuel, "depenses_mensuel": dep_mensuel}

def get_stats_depenses(d1=None, d2=None):
    conn = get_connection()
    c = conn.cursor()
    w = "WHERE 1=1"; p = []
    if d1: w += " AND DATE(date_depense)>=?"; p.append(d1)
    if d2: w += " AND DATE(date_depense)<=?"; p.append(d2)
    c.execute(f"""SELECT categorie, SUM(montant) as total, COUNT(*) as nombre
        FROM depenses {w} GROUP BY categorie ORDER BY total DESC""", p)
    par_cat = c.fetchall()
    c.execute(f"SELECT COALESCE(SUM(montant),0) as t FROM depenses {w}", p)
    total = c.fetchone()["t"]
    c.execute(f"""SELECT strftime(\'%Y-%m\',date_depense) as mois,
        SUM(montant) as total, COUNT(*) as nombre
        FROM depenses {w} GROUP BY mois ORDER BY mois""", p)
    par_mois = c.fetchall()
    conn.close()
    return {"total": total, "par_categorie": par_cat, "par_mois": par_mois}

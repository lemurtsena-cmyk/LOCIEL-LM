def create_zip():
    print("\n  Création du ZIP — Gestion Boutique Pro")
    print("  " + "="*42)

    # Dossiers à créer dans le ZIP
    DIRS = ["ui/", "utils/", "assets/", "factures/", "backup/"]
import sqlite3
import io
import struct

def create_empty_db():
    """Crée la base de données SQLite en mémoire et retourne les bytes"""
    
    # Créer DB en mémoire
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # ── Tables ──────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            description TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS fournisseurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            telephone TEXT,
            email TEXT,
            adresse TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
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
            FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            telephone TEXT,
            email TEXT,
            adresse TEXT,
            solde_credit REAL DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
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
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS details_ventes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vente_id INTEGER NOT NULL,
            produit_id INTEGER NOT NULL,
            quantite INTEGER NOT NULL,
            prix_unitaire REAL NOT NULL,
            sous_total REAL NOT NULL,
            FOREIGN KEY (vente_id) REFERENCES ventes(id),
            FOREIGN KEY (produit_id) REFERENCES produits(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS depenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            libelle TEXT NOT NULL,
            montant REAL NOT NULL,
            categorie TEXT,
            date_depense TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS achats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fournisseur_id INTEGER,
            date_achat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL,
            statut TEXT DEFAULT 'recu',
            notes TEXT,
            FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS details_achats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achat_id INTEGER NOT NULL,
            produit_id INTEGER NOT NULL,
            quantite INTEGER NOT NULL,
            prix_unitaire REAL NOT NULL,
            sous_total REAL NOT NULL,
            FOREIGN KEY (achat_id) REFERENCES achats(id),
            FOREIGN KEY (produit_id) REFERENCES produits(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS parametres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cle TEXT NOT NULL UNIQUE,
            valeur TEXT,
            description TEXT
        )
    """)

    # ── Données initiales ────────────────────────────────────
    # Catégories par défaut
    categories_defaut = [
        ("General",          "Categorie generale"),
        ("Alimentation",     "Produits alimentaires"),
        ("Boissons",         "Boissons diverses"),
        ("Hygiene",          "Produits hygiene et beaute"),
        ("Electromenager",   "Appareils electromenagers"),
        ("Vetements",        "Vetements et accessoires"),
        ("Informatique",     "Materiel informatique"),
        ("Papeterie",        "Fournitures de bureau"),
        ("Telephonie",       "Telephones et accessoires"),
        ("Autre",            "Autres produits"),
    ]
    for nom, desc in categories_defaut:
        c.execute(
            "INSERT OR IGNORE INTO categories (nom, description) VALUES (?,?)",
            (nom, desc)
        )

    # Fournisseur par défaut
    c.execute("""
        INSERT OR IGNORE INTO fournisseurs (nom, telephone, adresse)
        VALUES (?, ?, ?)
    """, ("Fournisseur General", "000 00 000 00", "Madagascar"))

    # Paramètres par défaut
    parametres_defaut = [
        ("boutique_nom",      "Ma Boutique",         "Nom de la boutique"),
        ("boutique_adresse",  "Madagascar",           "Adresse"),
        ("boutique_tel",      "000 00 000 00",        "Telephone"),
        ("boutique_email",    "contact@boutique.mg",  "Email"),
        ("monnaie",           "Ar",                   "Symbole monnaie"),
        ("monnaie_nom",       "Ariary",               "Nom monnaie"),
        ("tva",               "0",                    "TVA en %"),
        ("stock_alerte",      "5",                    "Seuil alerte stock"),
        ("facture_prefix",    "FAC",                  "Prefixe factures"),
        ("theme",             "dark",                 "Theme interface"),
        ("langue",            "fr",                   "Langue application"),
        ("backup_auto",       "1",                    "Sauvegarde automatique"),
        ("backup_frequence",  "7",                    "Frequence backup (jours)"),
        ("version_db",        "1.0.0",                "Version base de donnees"),
    ]
    for cle, val, desc in parametres_defaut:
        c.execute("""
            INSERT OR IGNORE INTO parametres (cle, valeur, description)
            VALUES (?,?,?)
        """, (cle, val, desc))

    # Produits de démonstration
    produits_demo = [
        ("PROD001", "Riz 5kg",          1,  None, 8000,  12000, 50, 10, "sac"),
        ("PROD002", "Huile 1L",         1,  None, 4500,  7000,  30, 5,  "litre"),
        ("PROD003", "Sucre 1kg",        1,  None, 2500,  4000,  40, 8,  "kg"),
        ("PROD004", "Farine 1kg",       1,  None, 2000,  3500,  25, 5,  "kg"),
        ("PROD005", "Savon Lux",        4,  None, 1200,  2000,  60, 10, "piece"),
        ("PROD006", "Eau Minerale 1.5L",2,  None, 800,   1500,  100,20, "piece"),
        ("PROD007", "Coca-Cola 33cl",   2,  None, 1000,  1800,  80, 15, "piece"),
        ("PROD008", "Cahier 100 pages", 8,  None, 1500,  2500,  45, 10, "piece"),
        ("PROD009", "Stylo Bic",        8,  None, 300,   600,   200,30, "piece"),
        ("PROD010", "Lait concentre",   1,  None, 2200,  3500,  35, 8,  "boite"),
    ]
    for code, nom, cat_id, f_id, pa, pv, stock, smin, unite in produits_demo:
        c.execute("""
            INSERT OR IGNORE INTO produits
            (code,nom,categorie_id,fournisseur_id,
             prix_achat,prix_vente,stock,stock_minimum,unite)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (code, nom, cat_id, f_id, pa, pv, stock, smin, unite))

    # Clients de démonstration
    clients_demo = [
        ("Rakoto Jean",     "034 12 345 67", "rakoto@email.mg",    "Antananarivo"),
        ("Rabe Marie",      "033 98 765 43", "rabe@email.mg",      "Fianarantsoa"),
        ("Randria Paul",    "032 11 222 33", "",                    "Toamasina"),
        ("Rasoa Nathalie",  "034 55 666 77", "rasoa@email.mg",     "Mahajanga"),
        ("Rakotondrabe",    "033 44 555 66", "",                    "Antsiranana"),
    ]
    for nom, tel, email, adr in clients_demo:
        c.execute("""
            INSERT OR IGNORE INTO clients (nom, telephone, email, adresse)
            VALUES (?,?,?,?)
        """, (nom, tel, email, adr))

    # Dépenses de démonstration
    from datetime import datetime, timedelta
    today = datetime.now()
    depenses_demo = [
        ("Loyer mensuel",        150000, "Loyer",
         (today - timedelta(days=5)).strftime("%Y-%m-%d"),
         "Loyer du mois"),
        ("Facture electricite",   45000, "Electricite",
         (today - timedelta(days=10)).strftime("%Y-%m-%d"),
         ""),
        ("Facture eau",           12000, "Eau",
         (today - timedelta(days=12)).strftime("%Y-%m-%d"),
         ""),
        ("Salaire employe",      200000, "Salaires",
         (today - timedelta(days=1)).strftime("%Y-%m-%d"),
         "Salaire du mois"),
        ("Transport marchandise", 25000, "Transport",
         (today - timedelta(days=3)).strftime("%Y-%m-%d"),
         "Livraison fournisseur"),
        ("Internet/Tel",          15000, "Internet/Telephone",
         (today - timedelta(days=8)).strftime("%Y-%m-%d"),
         "Abonnement mensuel"),
    ]
    for lib, mont, cat, date_, notes in depenses_demo:
        c.execute("""
            INSERT INTO depenses (libelle, montant, categorie,
                                  date_depense, notes)
            VALUES (?,?,?,?,?)
        """, (lib, mont, cat, date_, notes))

    conn.commit()

    # ── Sauvegarder en fichier temporaire puis lire les bytes ──
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile(
        suffix=".db", delete=False)
    tmp_path = tmp.name
    tmp.close()

    # Copier la DB en mémoire vers le fichier temporaire
    import sqlite3 as sq3
    conn2 = sq3.connect(tmp_path)
    conn.backup(conn2)
    conn2.close()
    conn.close()

    # Lire les bytes
    with open(tmp_path, "rb") as f:
        db_bytes = f.read()

    os.unlink(tmp_path)
    return db_bytes
    print("\n  Génération de la base de données...")
db_bytes = create_empty_db()
print(f"  ✅ boutique.db généré ({len(db_bytes)/1024:.1f} Ko)")

with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED,
                     compresslevel=9) as zf:

    # Dossiers
    DIRS = ["ui/", "utils/", "assets/", "factures/", "backup/"]
    for d in DIRS:
        zf.mkdir(f"GestionBoutique/{d}")
        print(f"  📁 Dossier: {d}")

    # ✅ Base de données incluse directement
    zf.writestr("GestionBoutique/boutique.db", db_bytes)
    print(f"  ✅ {'boutique.db':<40} ({len(db_bytes)//1024:>4} Ko) ← BASE DE DONNÉES")

    # Tous les fichiers .py et .txt et .bat
    for path, content in FILES.items():
        arc = f"GestionBoutique/{path}"
        zf.writestr(arc, content.encode("utf-8"))
        size = len(content.encode("utf-8"))
        print(f"  ✅ {path:<40} ({size:>6} octets)")

# ── Résumé final ──────────────────────────────────────────
final_size = os.path.getsize(ZIP_NAME) / 1024
print(f"""
  {'='*45}
  ✅ ZIP créé    : {ZIP_NAME}
  📦 Taille      : {final_size:.1f} Ko
  📄 Fichiers    : {len(FILES) + 1} (dont boutique.db)
  {'='*45}

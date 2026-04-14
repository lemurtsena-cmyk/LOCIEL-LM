╔══════════════════════════════════════════════════════════╗
║         GESTION BOUTIQUE PRO  —  v1.0.0                 ║
║              Application Desktop Offline                 ║
║              Format monétaire : Ariary (Ar)              ║
╚══════════════════════════════════════════════════════════╝

═══════════════════════════════════════════
  DÉMARRAGE RAPIDE
═══════════════════════════════════════════

  ÉTAPE 1 — Installer Python
  ───────────────────────────
  Téléchargez Python 3.10+ depuis:
  https://www.python.org/downloads/
  ✅ Cochez "Add Python to PATH" lors de l'installation!

  ÉTAPE 2 — Installer les dépendances
  ─────────────────────────────────────
  Double-cliquez sur: install.bat

  ÉTAPE 3 — Lancer l'application
  ────────────────────────────────
  Double-cliquez sur: run_dev.bat

  ÉTAPE 4 — Créer l'exécutable .exe (optionnel)
  ────────────────────────────────────────────────
  Double-cliquez sur: build_exe.bat
  → Votre .exe sera dans: dist/GestionBoutique_v1.0.0/

═══════════════════════════════════════════
  FONCTIONNALITÉS
═══════════════════════════════════════════

  ✅ Tableau de bord — statistiques temps réel
  ✅ Produits       — stock, catégories, prix en Ar
  ✅ Ventes         — caisse, factures PDF en Ar
  ✅ Clients        — gestion et historique
  ✅ Fournisseurs   — répertoire fournisseurs
  ✅ Dépenses       — suivi par catégorie + graphiques
  ✅ Rapports       — analyses complètes + export PDF/Excel
  ✅ Sauvegarde     — backup/restauration base de données
  ✅ 100% Offline   — aucune connexion requise

═══════════════════════════════════════════
  STRUCTURE DES FICHIERS
═══════════════════════════════════════════

  main.py          → Point d'entrée
  database.py      → Base de données SQLite
  build.py         → Script de compilation .exe
  ui/              → Interface graphique
  utils/           → Outils (PDF, backup, formatage)
  factures/        → Factures PDF générées
  backup/          → Sauvegardes automatiques
  boutique.db      → Base de données (créée au 1er lancement)

═══════════════════════════════════════════
  IMPORTANT — SAUVEGARDE
═══════════════════════════════════════════

  ⚠️  Le fichier boutique.db contient TOUTES vos données!
  Sauvegardez-le régulièrement via le menu Sauvegarde.

Version: 1.0.0  |  © 2024

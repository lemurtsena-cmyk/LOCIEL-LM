def create_zip():
    print("\n  Création du ZIP — Gestion Boutique Pro")
    print("  " + "="*42)

    # Dossiers à créer dans le ZIP
    DIRS = ["ui/", "utils/", "assets/", "factures/", "backup/"]

    with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as zf:
        # Dossiers vides
        for d in DIRS:
            zf.mkdir(f"GestionBoutique/{d}")
            print(f"  📁 Dossier: {d}")

        # Fichiers
        for path, content in FILES.items():
            arc = f"GestionBoutique/{path}"
            zf.writestr(arc, content.encode("utf-8"))
            size = len(content.encode("utf-8"))
            print(f"  ✅ {path:<40} ({size:>6} octets)")

    final_size = os.path.getsize(ZIP_NAME) / 1024
    print(f"\n  {'='*42}")
    print(f"  ✅ ZIP créé : {ZIP_NAME}")
    print(f"  📦 Taille   : {final_size:.1f} Ko")
    print(f"  📄 Fichiers : {len(FILES)}")
    print(f"  {'='*42}\n")

if __name__ == "__main__":
    create_zip()
    print("  Ouvrez le ZIP et suivez README.txt\n")

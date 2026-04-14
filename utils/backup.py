import os, shutil
from datetime import datetime
import database as db

BACKUP_DIR = os.environ.get("APP_BACKUP_DIR", "backup")

def create_backup(auto=False):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    prefix = "auto" if auto else "manuel"
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"boutique_{prefix}_{now}.db")
    shutil.copy2(db.DB_PATH, dest)
    _cleanup(10)
    return dest

def _cleanup(max_keep=10):
    files = sorted([
        os.path.join(BACKUP_DIR, f)
        for f in os.listdir(BACKUP_DIR) if f.endswith(".db")
    ], key=os.path.getmtime)
    while len(files) > max_keep:
        os.remove(files.pop(0))

def get_backups():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    files = []
    for f in os.listdir(BACKUP_DIR):
        if f.endswith(".db"):
            path = os.path.join(BACKUP_DIR, f)
            files.append({"nom": f, "chemin": path,
                "taille": os.path.getsize(path),
                "date": datetime.fromtimestamp(
                    os.path.getmtime(path)).strftime("%d/%m/%Y %H:%M")})
    return sorted(files, key=lambda x: x["date"], reverse=True)

def restore_backup(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Introuvable: {path}")
    shutil.copy2(path, db.DB_PATH)

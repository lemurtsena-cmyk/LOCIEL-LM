import os
import sys
import shutil
import subprocess
from pathlib import Path

APP_NAME    = "GestionBoutique"
APP_VERSION = "1.0.0"
APP_AUTHOR  = "Ma Boutique"
MAIN_SCRIPT = "main.py"
ICON_PATH   = "assets/logo.ico"
OUTPUT_DIR  = "dist"
BUILD_DIR   = "build"

class C:
    GREEN  = "\\033[92m"
    YELLOW = "\\033[93m"
    RED    = "\\033[91m"
    BLUE   = "\\033[94m"
    CYAN   = "\\033[96m"
    BOLD   = "\\033[1m"
    RESET  = "\\033[0m"

def log(msg, color=C.RESET):
    print(f"{color}{msg}{C.RESET}")

def step(num, total, msg):
    print(f"\\n{C.BOLD}{C.BLUE}[{num}/{total}]{C.RESET} {C.CYAN}{msg}{C.RESET}")

def ok(msg):   print(f"  {C.GREEN}OK  {msg}{C.RESET}")
def warn(msg): print(f"  {C.YELLOW}WARN {msg}{C.RESET}")
def err(msg):  print(f"  {C.RED}ERR  {msg}{C.RESET}")

TOTAL = 7

# ── ETAPE 1 ──────────────────────────────────────────────
def step1_check_python():
    step(1, TOTAL, "Verification Python")
    v = sys.version_info
    if v.major < 3 or v.minor < 8:
        err(f"Python 3.8+ requis. Actuel: {v.major}.{v.minor}")
        sys.exit(1)
    ok(f"Python {v.major}.{v.minor}.{v.micro}")

# ── ETAPE 2 ──────────────────────────────────────────────
def step2_install_deps():
    step(2, TOTAL, "Installation dependances")
    deps = ["PyQt5", "matplotlib", "reportlab",
            "pandas", "openpyxl", "Pillow", "pyinstaller"]
    for dep in deps:
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install",
                 dep, "--quiet"],
                capture_output=True, text=True)
            if result.returncode == 0:
                ok(f"Installe: {dep}")
            else:
                warn(f"Probleme avec {dep}")
        except Exception as e:
            err(f"Erreur {dep}: {e}")

# ── ETAPE 3 ──────────────────────────────────────────────
def step3_create_assets():
    step(3, TOTAL, "Creation des assets")
    os.makedirs("assets",   exist_ok=True)
    os.makedirs("factures", exist_ok=True)
    os.makedirs("backup",   exist_ok=True)

    ico = Path(ICON_PATH)
    if not ico.exists():
        warn("Icone absente -> generation icone par defaut")
        _create_icon()
        ok("Icone generee: assets/logo.ico")
    else:
        ok(f"Icone trouvee: {ICON_PATH}")

    _create_version_file()
    ok("version.txt cree")

def _create_icon():
    try:
        from PIL import Image, ImageDraw
        sizes = [16, 32, 48, 64, 128, 256]
        images = []
        for size in sizes:
            img = Image.new("RGBA", (size, size), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            m = size // 8
            draw.ellipse([m, m, size-m, size-m], fill="#2563eb")
            draw.text((size//2, size//2), "G",
                      fill="white", anchor="mm")
            images.append(img)
        images[0].save(ICON_PATH, format="ICO",
                       sizes=[(s,s) for s in sizes],
                       append_images=images[1:])
    except:
        _create_minimal_ico()

def _create_minimal_ico():
    import struct
    def bmp(size=16):
        w = h = size
        bi = struct.pack("<IiiHHIIiiII",
             40, w, -h, 1, 32, 0, w*h*4, 0, 0, 0, 0)
        px = b""
        for y in range(h):
            for x in range(w):
                cx,cy = x-w//2, y-h//2
                if cx*cx+cy*cy < (w//2-1)**2:
                    px += b"\\xff\\x63\\x25\\x89"
                else:
                    px += b"\\x00\\x00\\x00\\x00"
        return bi + px
    data = bmp(16)
    import struct as s
    hdr = s.pack("<HHH", 0, 1, 1)
    entry = s.pack("<BBBBHHII", 16,16,0,0,1,32,len(data),22)
    with open(ICON_PATH, "wb") as f:
        f.write(hdr + entry + data)

def _create_version_file():
    v = APP_VERSION.replace(".", ", ") + ", 0"
    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({v}),
    prodvers=({v}),
    mask=0x3f, flags=0x0, OS=0x40004,
    fileType=0x1, subtype=0x0, date=(0,0)),
  kids=[
    StringFileInfo([StringTable(u\'040C04B0\',[
      StringStruct(u\'CompanyName\',     u\'{APP_AUTHOR}\'),
      StringStruct(u\'FileDescription\', u\'Gestion Boutique Pro\'),
      StringStruct(u\'FileVersion\',     u\'{APP_VERSION}\'),
      StringStruct(u\'InternalName\',    u\'{APP_NAME}\'),
      StringStruct(u\'LegalCopyright\',  u\'Copyright 2024\'),
      StringStruct(u\'OriginalFilename\',u\'{APP_NAME}.exe\'),
      StringStruct(u\'ProductName\',     u\'Gestion Boutique Pro\'),
      StringStruct(u\'ProductVersion\',  u\'{APP_VERSION}\')])]),
    VarFileInfo([VarStruct(u\'Translation\',[0x040C,1200])])
  ]
)"""
    with open("version.txt", "w", encoding="utf-8") as f:
        f.write(content)

# ── ETAPE 4 ──────────────────────────────────────────────
def step4_clean():
    step(4, TOTAL, "Nettoyage builds precedents")
    for d in [BUILD_DIR, OUTPUT_DIR,
              "__pycache__", f"{APP_NAME}.spec"]:
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.rmtree(d)
            else:
                os.remove(d)
            ok(f"Supprime: {d}")
    for root, dirs, _ in os.walk("."):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))

# ── ETAPE 5 ──────────────────────────────────────────────
def step5_compile():
    step(5, TOTAL, "Compilation PyInstaller")

    hidden = [
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
        "PyQt5.QtPrintSupport",
        "matplotlib.backends.backend_qt5agg",
        "matplotlib.backends.backend_agg",
        "matplotlib.figure",
        "matplotlib.pyplot",
        "reportlab",
        "reportlab.lib",
        "reportlab.platypus",
        "reportlab.pdfgen",
        "pandas",
        "openpyxl",
        "openpyxl.styles",
        "sqlite3",
        "PIL",
        "pkg_resources.py2_warn",
    ]

    datas = [
        ("assets", "assets"),
        ("ui",     "ui"),
        ("utils",  "utils"),
    ]

    excludes = [
        "tkinter", "unittest", "test", "distutils",
        "PyQt5.QtBluetooth", "PyQt5.QtDesigner",
        "PyQt5.QtLocation",  "PyQt5.QtMultimedia",
        "PyQt5.QtNfc",       "PyQt5.QtQml",
        "PyQt5.QtQuick",     "PyQt5.QtSensors",
        "PyQt5.QtSerialPort","PyQt5.QtWebEngine",
        "PyQt5.QtWebKit",    "PyQt5.QtWebSockets",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        f"--name={APP_NAME}",
        "--windowed",
        "--onefile",
        f"--icon={ICON_PATH}",
        f"--version-file=version.txt",
        f"--distpath={OUTPUT_DIR}",
        f"--workpath={BUILD_DIR}",
    ]
    for h in hidden:
        cmd += ["--hidden-import", h]
    for src, dst in datas:
        if os.path.exists(src):
            cmd += ["--add-data", f"{src};{dst}"]
    for ex in excludes:
        cmd += ["--exclude-module", ex]
    cmd.append(MAIN_SCRIPT)

    log("  Compilation en cours (patientez 2-5 min)...", C.YELLOW)
    try:
        result = subprocess.run(cmd)
        if result.returncode == 0:
            ok("Compilation reussie!")
        else:
            err(f"Erreur compilation (code {result.returncode})")
            sys.exit(1)
    except FileNotFoundError:
        err("PyInstaller introuvable!")
        err("Lancez: pip install pyinstaller")
        sys.exit(1)

# ── ETAPE 6 ──────────────────────────────────────────────
def step6_post_process():
    step(6, TOTAL, "Organisation dossier final")

    exe = Path(OUTPUT_DIR) / f"{APP_NAME}.exe"
    if not exe.exists():
        err(f"Executable non trouve: {exe}")
        return None

    size_mb = exe.stat().st_size / (1024*1024)
    ok(f"Executable: {exe} ({size_mb:.1f} MB)")

    final = Path(OUTPUT_DIR) / f"{APP_NAME}_v{APP_VERSION}"
    final.mkdir(exist_ok=True)

    shutil.copy2(exe, final / f"{APP_NAME}.exe")

    for d in ["factures", "backup", "assets"]:
        (final / d).mkdir(exist_ok=True)
    if os.path.exists("assets"):
        shutil.copytree("assets", final / "assets",
                        dirs_exist_ok=True)

    _create_readme(final)
    _create_bat(final)

    ok(f"Dossier final: {final.absolute()}")
    return final

def _create_readme(folder):
    txt = f"""╔══════════════════════════════════════╗
║   GESTION BOUTIQUE PRO  v{APP_VERSION}        ║
║   Application Desktop 100% Offline   ║
╚══════════════════════════════════════╝

LANCEMENT
─────────
Double-cliquez sur {APP_NAME}.exe

SAUVEGARDE IMPORTANTE
──────────────────────
Le fichier boutique.db contient TOUTES vos donnees.
Sauvegardez-le regulierement!

DOSSIERS
─────────
{APP_NAME}.exe  → Application
factures/       → Factures PDF
backup/         → Sauvegardes
boutique.db     → Base de donnees (cree au 1er lancement)

Version {APP_VERSION}  |  Format monetaire: Ariary (Ar)
"""
    with open(folder / "README.txt", "w", encoding="utf-8") as f:
        f.write(txt)

def _create_bat(folder):
    bat = f"""@echo off
cd /d "%~dp0"
{APP_NAME}.exe
if errorlevel 1 (
    echo ERREUR au lancement!
    pause
)
"""
    with open(folder / "Lancer.bat", "w") as f:
        f.write(bat)

# ── ETAPE 7 ──────────────────────────────────────────────
def step7_nsis():
    step(7, TOTAL, "Installateur NSIS (optionnel)")
    nsis_paths = [
        r"C:\\Program Files (x86)\\NSIS\\makensis.exe",
        r"C:\\Program Files\\NSIS\\makensis.exe",
    ]
    nsis = next((p for p in nsis_paths if os.path.exists(p)), None)

    _write_nsis_script()

    if nsis:
        try:
            subprocess.run([nsis, "installer.nsi"], check=True)
            ok(f"Installateur: {APP_NAME}_Setup_v{APP_VERSION}.exe")
        except subprocess.CalledProcessError:
            warn("Erreur NSIS")
    else:
        warn("NSIS non installe -> installateur ignore")
        warn("https://nsis.sourceforge.io/ (optionnel)")

def _write_nsis_script():
    script = f"""
Unicode True
!define APP   "{APP_NAME}"
!define VER   "{APP_VERSION}"
!define EXE   "{APP_NAME}.exe"
!define DIR   "$PROGRAMFILES\\\\{APP_NAME}"
!define REG   "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Uninstall\\\\{APP_NAME}"

Name "${{APP}} v${{VER}}"
OutFile "dist\\\\{APP_NAME}_Setup_v{APP_VERSION}.exe"
InstallDir "${{DIR}}"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

!include "MUI2.nsh"
!define MUI_ICON "assets\\\\logo.ico"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "French"

Section "App" S01
  SetOutPath "$INSTDIR"
  File "dist\\\\{APP_NAME}_v{APP_VERSION}\\\\${{EXE}}"
  File "dist\\\\{APP_NAME}_v{APP_VERSION}\\\\README.txt"
  CreateDirectory "$INSTDIR\\\\factures"
  CreateDirectory "$INSTDIR\\\\backup"
  CreateShortCut "$DESKTOP\\\\${{APP}}.lnk" "$INSTDIR\\\\${{EXE}}"
  CreateDirectory "$SMPROGRAMS\\\\${{APP}}"
  CreateShortCut "$SMPROGRAMS\\\\${{APP}}\\\\${{APP}}.lnk" "$INSTDIR\\\\${{EXE}}"
  CreateShortCut "$SMPROGRAMS\\\\${{APP}}\\\\Desinstaller.lnk" "$INSTDIR\\\\Uninstall.exe"
  WriteRegStr   HKLM "${{REG}}" "DisplayName"     "${{APP}}"
  WriteRegStr   HKLM "${{REG}}" "DisplayVersion"  "${{VER}}"
  WriteRegStr   HKLM "${{REG}}" "UninstallString" "$INSTDIR\\\\Uninstall.exe"
  WriteUninstaller "$INSTDIR\\\\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\\\\${{EXE}}"
  Delete "$INSTDIR\\\\README.txt"
  Delete "$INSTDIR\\\\boutique.db"
  Delete "$INSTDIR\\\\Uninstall.exe"
  RMDir /r "$INSTDIR\\\\factures"
  RMDir /r "$INSTDIR\\\\backup"
  RMDir "$INSTDIR"
  Delete "$DESKTOP\\\\${{APP}}.lnk"
  RMDir /r "$SMPROGRAMS\\\\${{APP}}"
  DeleteRegKey HKLM "${{REG}}"
SectionEnd
"""
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(script)
    ok("installer.nsi cree")

# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════
def main():
    print(f"""
{C.BOLD}{C.BLUE}╔══════════════════════════════════════╗
║  BUILD — Gestion Boutique Pro        ║
║  Generation executable Windows       ║
╚══════════════════════════════════════╝{C.RESET}
""")
    step1_check_python()
    step2_install_deps()
    step3_create_assets()
    step4_clean()
    step5_compile()
    final = step6_post_process()
    step7_nsis()

    if final:
        print(f"""
{C.BOLD}{C.GREEN}╔══════════════════════════════════════╗
║        BUILD TERMINE AVEC SUCCES!    ║
╚══════════════════════════════════════╝{C.RESET}

{C.CYAN}Executable:{C.RESET}
  {C.GREEN}dist/{APP_NAME}_v{APP_VERSION}/{APP_NAME}.exe{C.RESET}

{C.CYAN}Contenu du dossier:{C.RESET}
  {APP_NAME}.exe
  README.txt
  Lancer.bat
  factures/
  backup/

{C.YELLOW}Distribuez le DOSSIER complet, pas seulement le .exe !{C.RESET}
""")

if __name__ == "__main__":
    main()

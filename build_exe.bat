@echo off
chcp 65001 >nul
cls
echo.
echo  ==========================================
echo   BUILD — Gestion Boutique Pro
echo  ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  ERREUR: Python non trouve!
    echo  Installez Python depuis https://python.org
    pause & exit /b 1
)

echo  Lancement du build...
python build.py

if errorlevel 1 (
    echo.
    echo  ERREUR lors du build!
    pause & exit /b 1
)

echo.
echo  BUILD TERMINE!
echo  Votre .exe est dans: dist\\GestionBoutique_v1.0.0\\
echo.
explorer dist\\GestionBoutique_v1.0.0 2>nul
pause

@echo off
chcp 65001 >nul
cls
echo.
echo  ==========================================
echo   INSTALLATION — Gestion Boutique Pro
echo  ==========================================
echo.
echo  Installation des dependances Python...
echo.

pip install PyQt5 matplotlib reportlab pandas openpyxl Pillow pyinstaller

echo.
echo  ==========================================
echo   INSTALLATION TERMINEE!
echo  ==========================================
echo.
echo  Pour lancer l'application:  double-clic sur run_dev.bat
echo  Pour creer le .exe:         double-clic sur build_exe.bat
echo.
pause

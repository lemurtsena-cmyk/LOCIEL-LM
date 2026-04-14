@echo off
chcp 65001 >nul
echo Lancement mode developpement...
python main.py
if errorlevel 1 ( echo ERREUR! & pause )

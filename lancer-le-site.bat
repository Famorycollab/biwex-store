@echo off
REM ============================================================
REM  LANCEMENT FACILE DU SITE BIWEX STORE DANS DOCKER
REM  Auteurs : Famory TOURE & Abdoul TRAORE - ISG Sousse
REM ============================================================

echo.
echo ============================================================
echo   DEMARRAGE DU SITE BIWEX STORE EN CONTENEUR DOCKER
echo ============================================================
echo.

REM 1. Verifie si le conteneur existe deja et le relance, ou le cree
docker rm -f biwex-production 2>NUL

echo [Docker] Demarrage du conteneur sur le port 5000...
docker run -d --name biwex-production -p 5000:5000 -e SECRET_KEY=biwex-prod-secret biwex-store:latest

if errorlevel 1 (
    echo.
    echo [ERREUR] Impossible de lancer Docker !
    echo Verifiez que l'application Docker Desktop est bien ouverte.
    echo.
    pause
    exit /b 1
)

echo.
echo [Succes] Le conteneur tourne parfaitement !
echo [Info] Ouverture automatique de votre navigateur sur http://localhost:5000 ...
echo.

REM 2. Ouvre le site web automatiquement dans votre navigateur par defaut
start http://localhost:5000

echo Appuyez sur une touche pour fermer cette fenetre...
pause >NUL

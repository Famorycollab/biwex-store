@echo off
REM ============================================================
REM  SCRIPT DE CONFIGURATION DU WORKFLOW GIT - BIWEX STORE
REM  Auteurs : Famory TOURE & Abdoul TRAORE
REM
REM  Ce script configure les branches localement et pousse
REM  tout vers GitHub pour démarrer le workflow DevOps.
REM
REM  Structure des branches :
REM    main     : Production (protégée)
REM    dev      : Intégration (protégée)
REM    feature/ : Développement de fonctionnalités
REM
REM  Usage : scripts\setup-git.bat
REM ============================================================

echo.
echo =========================================================
echo   BIWEX STORE - Configuration du Workflow Git
echo   Auteurs : Famory TOURE et Abdoul TRAORE
echo =========================================================
echo.

REM ── Vérification qu'on est dans un dépôt Git ──────────────
git status >NUL 2>&1
if errorlevel 1 (
    echo ERREUR : Ce dossier n est pas un depot Git.
    echo Executez d abord : git init
    pause
    exit /b 1
)

echo [Git] Depot Git detecte. OK
echo.

REM ── Configuration de l'identité Git ──────────────────────
echo [Git] Configuration de l identite Git...
git config user.name "Famory TOURE"
git config user.email "famory@biwex.tn"

REM ── Commit initial si nécessaire ─────────────────────────
echo [Git] Ajout de tous les fichiers...
git add -A

echo [Git] Commit initial...
git commit -m "feat: initialisation complete du projet DevOps Biwex Store

- Application Flask e-commerce complete (app.py, database.py)
- 3 pipelines Jenkins (PR, dev, tag vX.Y.Z)
- Dockerfile multi-stage (Python 3.11/3.12)
- Smoke test ameliore avec rapport detaille
- README DevOps complet
- .gitignore et .dockerignore configures

Auteurs: Famory TOURE et Abdoul TRAORE
Projet: Introduction au DevOps - 3LIG" 2>NUL

echo.

REM ── Créer et pousser la branche dev ──────────────────────
echo [Git] Creation de la branche dev...
git branch dev 2>NUL
git checkout dev

echo [Git] Push de la branche dev vers GitHub...
git push -u origin dev

REM ── Revenir sur main ─────────────────────────────────────
git checkout main
echo [Git] Push de main vers GitHub...
git push -u origin main

echo.
echo [Git] Creation d une branche feature exemple...
git checkout -b feature/amelioration-pipeline
git checkout dev

echo.
echo =========================================================
echo   CONFIGURATION TERMINEE !
echo.
echo   Branches configurees :
echo     main              (protegee - production)
echo     dev               (protegee - integration)
echo     feature/amelioration-pipeline (exemple)
echo.
echo   Prochaines etapes :
echo   1. Allez sur GitHub et protegez les branches main et dev
echo   2. Configurez Jenkins avec les 3 Jenkinsfiles
echo   3. Creez une PR de feature/xxx vers dev pour tester
echo      le Pipeline 1 (Jenkinsfile-PR)
echo   4. Mergez vers dev pour declencher le Pipeline 2
echo   5. Creez un tag : git tag v1.0.0 et git push origin v1.0.0
echo      pour declencher le Pipeline 3 (Jenkinsfile-Tag)
echo =========================================================
echo.

pause

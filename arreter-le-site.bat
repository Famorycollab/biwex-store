@echo off
REM ============================================================
REM  ARRET DU CONTENEUR BIWEX STORE
REM ============================================================

echo.
echo Arret du site Biwex Store...
docker stop biwex-production 2>NUL
docker rm -f biwex-production 2>NUL
echo [OK] Conteneur arrete avec succes.
echo.
timeout /t 2 /nobreak >NUL

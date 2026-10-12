@echo off
chcp 65001 > nul
echo =======================================================
echo   Sincronizando con GitHub y Desplegando en Vercel
echo =======================================================
cd /d "%~dp0"

set MENSAJE=%*
if "%MENSAJE%"=="" set MENSAJE=actualizacion y mejoras del proyecto

echo [1/3] Preparando archivos modificados (git add)...
git add .

echo [2/3] Registrando version (git commit)...
git commit -m "%MENSAJE%"

echo [3/3] Subiendo a GitHub en la rama main (git push)...
git push origin main

echo.
echo =======================================================
echo   ¡ÉXITO! Cambios subidos a GitHub.
echo   Vercel ya inicio el despliegue automatico.
echo   Tu web en vivo estara lista en unos 30 segundos.
echo =======================================================
pause


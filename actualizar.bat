@echo off
chcp 65001 > nul
echo =======================================================
echo   Subiendo cambios a GitHub en la rama dev
echo =======================================================
cd /d "%~dp0"

set MENSAJE=%*
if "%MENSAJE%"=="" set MENSAJE=actualizacion y mejoras del proyecto

echo [1/4] Cambiando a la rama dev (git checkout dev)...
git checkout dev
if errorlevel 1 (
  echo ERROR: no se pudo cambiar a dev. Revisa que no haya conflictos pendientes.
  pause
  exit /b 1
)

echo [2/4] Preparando archivos modificados (git add)...
git add -A
git status --short

echo [3/4] Registrando version (git commit)...
git commit -m "%MENSAJE%"

echo [4/4] Subiendo a GitHub en la rama dev (git push)...
git push origin dev
if errorlevel 1 (
  echo ERROR: no se pudo subir a GitHub.
  pause
  exit /b 1
)

echo.
echo =======================================================
echo   Cambios subidos a la rama dev.
echo   Para publicarlos en produccion (Vercel), abre un
echo   Pull Request de dev hacia main en GitHub y fusionalo:
echo   https://github.com/mavalosc/control-neumaticos-caex/compare/main...dev
echo =======================================================
pause

@echo off
setlocal
rem Native Windows checkout launcher. Installed packages get a normal um.exe entry point.
where uv >nul 2>nul
if %errorlevel% equ 0 (
  uv run --quiet --project "%~dp0.." --extra mcp python -m um %*
  exit /b
)
set "PYTHONPATH=%~dp0..;%PYTHONPATH%"
python -m um %*

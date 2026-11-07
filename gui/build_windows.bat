@echo off
setlocal
cd /d "%~dp0.."
python -m venv .venv-build 2>nul
call .venv-build\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r gui\requirements-build.txt
pyinstaller --noconfirm --windowed --name "%~n1" gui\app.py
echo Build done: dist\%~n1\

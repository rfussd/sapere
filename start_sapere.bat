@echo off
cd /d "%~dp0"
echo 🧠 Iniciando Sapere...
echo.
echo No cierres esta ventana mientras estudias.
echo La pagina se abrira en tu navegador automaticamente.
echo.
py -m streamlit run main.py
pause

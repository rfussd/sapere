@echo off
cd /d "C:\Users\PRIDE BEETLE BLACK\sapere"
echo 🧠 Iniciando Sapere...
start http://localhost:8501
py -m streamlit run main.py --server.headless true
pause

@echo off
:: create env
echo # Creating environment
python -m venv .venv
:: use env
call .\.venv\Scripts\activate.bat
:: install libr
echo # Installing library needed
python -m pip install -r reqlibrary.txt
:: clear screen
cls
:: run web
python -m streamlit run index.py
pause

pip install -r requirements.txt
pyinstaller --onefile main.py
cd dist
del pycman.exe
rename main.exe pycman.exe
cd ..
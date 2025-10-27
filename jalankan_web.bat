@echo off
cd /d "D:\Mahasiswa\Semester 5\ambaba"
start "" "C:\Program Files\Python311\python.exe" "coba flask.py"
timeout /t 3 >nul
start "" http://192.168.110.10:5000
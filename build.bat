@echo off
nuitka ^
--msvc="latest" ^
--standalone ^
--disable-console ^
--include-data-dir=".\src\assets=.\assets" ^
--enable-plugin=pyside6 ^
--nofollow-import-to=tkinter ^
--output-filename="DRIP.exe" ^
".\src\main.py"

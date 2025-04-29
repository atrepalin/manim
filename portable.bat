@echo off

chcp 65001 > NUL

echo [INFO] Установка пути до файлов MikTeX...
set MIKTEX_BIN=%~dp0miktex\texmfs\install\miktex\bin\x64
echo [DONE] Путь установлен в %MIKTEX_BIN%
echo:

echo [INFO] Установка пути до интерпретатора Python...
SET PY=%~dp0python\bin\python.exe
echo [DONE] Путь установлен в %PY%
echo:

echo [INFO] Установка пути до пакетов Python...
SET PYTHONPATH=%~dp0venv\Lib\site-packages
echo [DONE] Путь установлен в %PYTHONPATH%
echo:

echo [INFO] Установка пути для точки входа...
SET APP=%~dp0main.py
echo [DONE] Путь установлен в %APP%
echo:

echo [INFO] Запуск...
%PY% %APP%
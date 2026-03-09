@echo off
echo ===============================
echo LIMPIANDO PROYECTO DJANGO
echo ===============================

cd backend

echo.
echo Eliminando migraciones...

for /d %%d in (*) do (
    if exist "%%d\migrations" (
        del /q "%%d\migrations\0*.py"
        del /q "%%d\migrations\1*.py"
        del /q "%%d\migrations\2*.py"
        del /q "%%d\migrations\3*.py"
        del /q "%%d\migrations\4*.py"
        del /q "%%d\migrations\5*.py"
        del /q "%%d\migrations\6*.py"
        del /q "%%d\migrations\7*.py"
        del /q "%%d\migrations\8*.py"
        del /q "%%d\migrations\9*.py"
    )
)

echo.
echo Eliminando cache python...

for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo.
echo Creando migraciones nuevas...

python manage.py makemigrations

echo.
echo Aplicando migraciones...

python manage.py migrate

echo.
echo ===============================
echo PROYECTO LIMPIO
echo ===============================

pause
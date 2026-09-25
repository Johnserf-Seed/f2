@echo off
chcp 65001
REM Translation sources live next to the compiled catalogs:
REM f2\languages\LOCALE\LC_MESSAGES\LOCALE.po is compiled into LOCALE.mo

REM Extract messages (file names only, so moving code around does not touch the .po files)
echo [INFO] Extracting messages...
pybabel extract -F babel.cfg --add-location=file -o messages.pot f2 tests
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to extract messages.
    exit /b %ERRORLEVEL%
)

FOR %%L IN (en_US zh_CN) DO (
    REM Update translations
    echo [INFO] Updating f2\languages\%%L\LC_MESSAGES\%%L.po...
    pybabel update -i messages.pot -o f2\languages\%%L\LC_MESSAGES\%%L.po -l %%L
    IF ERRORLEVEL 1 (
        echo Error: Failed to update %%L.po.
        exit /b 1
    )

    REM Compile translations
    echo [INFO] Compiling f2\languages\%%L\LC_MESSAGES\%%L.mo...
    pybabel compile -i f2\languages\%%L\LC_MESSAGES\%%L.po -o f2\languages\%%L\LC_MESSAGES\%%L.mo -l %%L --statistics
    IF ERRORLEVEL 1 (
        echo Error: Failed to compile %%L.mo.
        exit /b 1
    )
)

echo [SUCCESS] Done.

@echo off
chcp 65001
REM Extract messages
echo [INFO] Extracting messages...
pybabel extract -F babel.cfg -o messages.pot .
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to extract messages.
    exit /b %ERRORLEVEL%
)

REM Update translations
echo [INFO] Updating translations...

REM Update en_US.po file and redirect logs
echo [INFO] Updating en_US.po...
msgmerge -U en_US.po messages.pot > msgmerge_en_US.log 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to update en_US.po. See msgmerge_en_US.log for details.
    exit /b %ERRORLEVEL%
)

REM Update zh_CN.po file
echo [INFO] Updating zh_CN.po...
msgmerge -U zh_CN.po messages.pot > msgmerge_zh_CN.log 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to update zh_CN.po. See msgmerge_zh_CN.log for details.
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] Done.

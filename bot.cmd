@ECHO OFF

SET BOT_DIR="%~dp0bot"

ECHO Entering %BOT_DIR%
PUSHD %BOT_DIR%
python3 5916024152.py
POPD

pause

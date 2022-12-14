@ECHO OFF


REM Predefined parameters:
SET APP_DIR="%~dp0app"
SET RESULT_DIR="..\result"
SET CONFIG_FILE="..\data\coalitions_demo.json"
SET MISSION_FILE="..\data\HAW_StalingradNorth_Graph\HAW_StalingradNorth_Graph.Mission"


REM DO NOT EDIT BELOW THIS LINE
REM ---------------------------
ECHO Entering %APP_DIR%
PUSHD %APP_DIR%
SET argCount=0
SET done=0
FOR %%x IN (%*) DO SET /A argCount+=1
IF %argCount% EQU 0 (
  ECHO Parse local files...
  python3 parser.py --mission-in-file "%MISSION_FILE%" ^
                    --config-in-file "%CONFIG_FILE%" ^
                    --mission-out-file "%RESULT_DIR%\FrontLine.Mission" ^
                    --mission-img-file "%RESULT_DIR%\FrontLine.png"
  SET done=1
)
IF %argCount% EQU 1 (
  ECHO Parse mission file...
  python3 parser.py --mission-in-file %1 ^
                    --config-in-file "%CONFIG_FILE%" ^
                    --mission-out-file "%RESULT_DIR%\FrontLine.Mission" ^
                    --mission-img-file "%RESULT_DIR%\FrontLine.png"
  SET done=1
)
IF %done% EQU 1 (
  ECHO Done!
) ELSE (
  ECHO.
  ECHO Usage:
  ECHO   - To create Front Line drop one ".Mission" file
  ECHO.
  python3 parser.py
  pause
)
POPD

pause
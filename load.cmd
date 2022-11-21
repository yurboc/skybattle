@ECHO OFF

REM How to use predefined parameters:
REM SET MISSION_IN="data/HAW_StalingradNorth_Graph/HAW_StalingradNorth_Graph.Mission"
REM SET MISSION_OUT="result/out.Mission"
REM python parser.py --mission-in-file %MISSION_IN% --mission-out-file %MISSION_OUT%

PUSHD %~dp0
SET argCount=0
SET done=0
FOR %%x IN (%*) DO SET /A argCount+=1
IF %argCount% EQU 1 (
  ECHO Parse mission file...
  python3 parser.py --mission-in-file %1 --coal-json-file "result/test_coalitions.json"
  SET done=1
)
IF %argCount% EQU 2 (
  ECHO Parse and create front line...
  python3 parser.py --mission-in-file %1 --mission-out-file %2 --front-line
  SET done=1
)
IF %done% EQU 1 (
  ECHO Done!
) ELSE (
  ECHO.
  ECHO Usage:
  ECHO   - Parse 1 Mission file  : drop one ".Mission" file
  ECHO   - Create Front line     : drop two ".Mission" files
  ECHO.
  python3 parser.py
  pause
)
POPD

pause
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
  python3 parser.py --mission-in-file %1 ^
                    --coal-json-file "result/test_coalitions.json" ^
                    --mission-out-file "result/FrontLine.Mission" ^
                    --mission-img-file "result/FrontLine.png"
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
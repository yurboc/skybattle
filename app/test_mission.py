import pytest

import filecmp
import os

from mission import Mission

RESULT_DIR="result"
CONFIG_FILE="data/coalitions_demo.json"
MISSION_FILE_IN="data/HAW_StalingradNorth_Graph/HAW_StalingradNorth_Graph.Mission"
MISSION_FILE_OUT="result/test_result.Mission"
MISSION_FILE_ETH="data/ethalon/ethalon_FrontLine.Mission"

def setup():
    # Check files
    assert os.path.exists(RESULT_DIR)
    assert os.path.exists(CONFIG_FILE)
    assert os.path.exists(MISSION_FILE_IN)
    assert os.path.exists(MISSION_FILE_ETH)
    print ("Basic setup done")
 
def teardown():
    # Remove files
    try:
        os.remove(MISSION_FILE_OUT)
    except OSError:
        print ("Can't remove output file!")
    print ("Basic teardown done")

def test_calculate_mission():
    # Parse input file
    mission = Mission()
    mission.loadMissionFromFile(MISSION_FILE_IN)

    # Print parsing results
    mission.printMissionStat()

    # Load Indexes, Coalitions and Forces from JSON
    mission.loadCoalitionForceJson(CONFIG_FILE)
    mission.updateOrigMission()

    # Prepare Front Line
    mission.calcFrontLinePairs()
    mission.calcFrontLine()
    mission.directFrontLine()
    mission.frontLineToString()
    mission.saveFrontLineToFile(MISSION_FILE_OUT)

    # Compare generated file with ethalon
    assert filecmp.cmp(MISSION_FILE_OUT, MISSION_FILE_ETH, shallow=False)

import argparse
import sys
import os

from mission import Mission

if __name__ == '__main__':
    # Prepare all arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--mission-in-file', type=str, dest='mis_in', action='store', help='Path to input mission file')
    parser.add_argument('-o', '--mission-out-file', type=str, dest='mis_out', action='store', help='Path to output mission file')
    parser.add_argument('-c', '--coal-json-file', type=str, dest='coal_out', action='store', help='Path to output coalitions JSON')

    # Show help if no arguments provided
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Parse arguments
    args = parser.parse_args()
    mission_in_path = args.mis_in
    mission_out_path = args.mis_out
    coalitions_out_path = args.coal_out

    # Check files
    if not os.path.exists(mission_in_path):
        print(f"Input file is not found: {mission_in_path}")
        exit()
    
    # Parse input file
    mission = Mission()
    mission.loadMissionFromFile(mission_in_path)

    # Print parsing results
    mission.printMissionStat()

    # Save Indexes, Coalitions and Forces to JSON
    mission.calcCoalitionAndForce()
    mission.saveCoalitionForceJson(coalitions_out_path)

    # Prepare Front Line
    mission.calcFrontLinePairs()
    mission.calcFrontLine()
    mission.directFrontLine()
    mission.frontLineToString()
    #mission.printFrontLineAsString()
    mission.saveFrontLineToFile(mission_out_path)

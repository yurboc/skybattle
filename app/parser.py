import argparse
import sys
import os
import logging

from mission import Mission

def main(mission_in_path, mission_out_path, mission_img_path, config_in_path):
    # Check files
    if not os.path.exists(mission_in_path):
        logging.debug(f"Input file is not found: {mission_in_path}")
        exit()
    
    # Parse input file
    mission = Mission()
    mission.loadMissionFromFile(mission_in_path)

    # Print parsing results
    mission.printMissionStat()

    # Save Indexes, Coalitions and Forces to JSON
    #mission.calcCoalitionAndForce()
    #mission.saveCoalitionForceJson(config_in_path)
    mission.loadCoalitionForceJson(config_in_path)
    mission.updateOrigMission()

    # Prepare Front Line
    logging.debug("Start parsing")
    mission.calcFrontLinePairs()
    mission.calcFrontLine()
    mission.directFrontLine()
    mission.frontLineToString()
    #mission.printFrontLineAsString()
    mission.saveFrontLineToFile(mission_out_path)
    mission.calcVisual()
    mission.plotVisual()
    mission.saveVisual(mission_img_path)
    logging.debug("Parsing complete")

if __name__ == '__main__':
    # Prepare logging
    logging.basicConfig(
        filename='../result/parser.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG,
    )

    # Prepare all arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--mission-in-file', type=str, dest='mis_in', action='store', help='Path to input mission file')
    parser.add_argument('-o', '--mission-out-file', type=str, dest='mis_out', action='store', help='Path to output mission file')
    parser.add_argument('-v', '--mission-img-file', type=str, dest='mis_img', action='store', help='Path to mission visualization')
    parser.add_argument('-c', '--config-in-file', type=str, dest='conf_in', action='store', help='Path to input JSON config')

    # Show help if no arguments provided
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Parse arguments
    args = parser.parse_args()
    mission_in_path = args.mis_in
    mission_out_path = args.mis_out
    mission_img_path = args.mis_img
    config_in_path = args.conf_in

    # Run main
    main(mission_in_path, mission_out_path, mission_img_path, config_in_path)

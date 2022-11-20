import argparse
import sys
import os

from mission import Mission

if __name__ == '__main__':
    # Prepare all arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--mission-in-file', type=str, dest='file_in', action='store', help='Path to input mission file')
    parser.add_argument('-o', '--mission-out-file', type=str, dest='file_out', action='store', help='Path to output mission file')
    parser.add_argument('-f', '--front-line', dest='do_front_line', action='store_true', default=False, help='Generate front line')

    # Show help if no arguments provided
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Parse arguments
    args = parser.parse_args()
    file_in_path = args.file_in
    file_out_path = args.file_out

    #file_a_name = 'HAW_StalingradNorth_Graph.Mission'
    #file_b_name = 'result.Mission'
    #file_a_path = os.path.join(CONT_DIR, file_a_name)

    # Check files
    if not os.path.exists(file_in_path):
        print(f"Input file is not found: {file_in_path}")
        exit()
    
    # Parse input file
    mission = Mission()
    mission.loadMissionFromFile(file_in_path)

    # Print parsing results
    mission.printMissionStat()

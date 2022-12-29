import os
import json
import math
import copy
import logging

from options import Options
from mcu_icon import MCU_Icon
from vizualization import Vizualization

class Mission:
    def __init__(self):
        self.options = Options()
        self.visual = Vizualization()
        self.mcuIconsArr = []
        self.mcuIconsDict = dict()
        self.coalitionsAndForce = dict()
        self.frontLineMcuIconPairs = []
        self.frontLineMcuIconsArr = []
        self.frontLineMcuIconsDict = dict()
        self.frontLineString = ""
        self.startFrontLineId = 1000
        self.ignoredOptions = [
            "Def_Force",
            "Conn_Targets",
            "Conn_Hint",
            "Rev_Targets",
            "FrontLine_Targets",
        ]
        self.replacedOptions = {"LineType": 13}
    
    def loadMissionFromFile(self, filePath):
        # Load Options from file
        self.options.loadOptionsFromFile(filePath)

        # Load all MCU_Icon from file
        self.mcuIconsArr = []
        self.mcuIconsDict = dict()
        itemsCount = 0
        logging.debug(f"Load MCU_Icon items from file: {os.path.basename(filePath)}")
        with open(filePath, "r") as f:
            fileLines = f.readlines()
            foundMCU = False
            currentMcuStr = ""
            for line in fileLines:
                # Before "MCU_Icon" block
                if not foundMCU and not line.startswith("MCU_Icon"):
                    continue
                # Begin "MCU_Icon" block
                if not foundMCU and line.startswith("MCU_Icon"):
                    foundMCU = True
                    continue
                # Inside "MCU_Icon" block
                if not line.startswith("}"):
                    currentMcuStr += line
                    continue
                # End of "Options" block
                if line.startswith("}"):
                    currentMcuStr += line
                    currentMcuIcon = MCU_Icon(currentMcuStr)
                    currentMcuIcon.parse()
                    self.mcuIconsArr.append(currentMcuIcon)
                    self.mcuIconsDict[currentMcuIcon.options["Index"]] = currentMcuIcon
                    itemsCount += 1
                    currentMcuStr = ""
                    foundMCU = False
                    continue
        logging.debug(f"Load MCU_Icon done: {itemsCount} items")

    def printMissionStat(self):
        logging.debug(f"===== BEGIN =====")
        logging.debug(f"Has Options    : {self.options.hasData()}")
        logging.debug(f"MCU_Icon count : {len(self.mcuIconsArr)} total, {len(self.mcuIconsDict)} unique")
        #logging.debug(f"==== OPTIONS ====")
        #self.options.printRawData()
        #logging.debug(f"=== MCU_ICONS ===")
        #self.mcuIcons[0].printRawData()
        logging.debug(f"====== END ======")

    def calcCoalitionAndForce(self):
        self.coalitionsAndForce = dict()
        for mcuIcon in self.mcuIconsArr:
            curIndex = int(mcuIcon.options['Index'])
            curCoalition = mcuIcon.options['Coalitions'][0]
            curForce = 50
            self.coalitionsAndForce[curIndex] = {"coalition": curCoalition, "force": curForce}
        logging.debug("Coalitions calculated!")

    def saveCoalitionForceJson(self, filePath):
        resJson = json.dumps(self.coalitionsAndForce, indent=2)
        with open(filePath, "w") as f:
            f.write(resJson)
        logging.debug("Coalitions saved to JSON!")

    def loadCoalitionForceJson(self, filePath):
        self.coalitionsAndForce = dict()
        with open(filePath, "r") as f:
            inJsonStr = f.read()
            self.coalitionsAndForce = json.loads(inJsonStr,
                object_hook=lambda d: {  int(k) if k.lstrip('-').isdigit()
                                                else k: v for k, v in d.items()})
        logging.debug("Coalitions loaded from JSON!")

    def updateOrigMission(self):
        for mcuIcon in self.mcuIconsArr:
            curIndex = int(mcuIcon.options['Index'])
            mcuIconParams = self.coalitionsAndForce[curIndex]
            mcuIcon.options['Coalitions'] = [mcuIconParams["coalition"]]
            mcuIcon.options['Def_Force'] = mcuIconParams["force"]

    def calcFrontLinePairs(self):
        self.frontLineMcuIconPairs = []
        pairsCount = 0
        for mcuIcon in self.mcuIconsArr:
            curIndex = int(mcuIcon.options['Index'])
            curCoalition = self.coalitionsAndForce[curIndex]["coalition"]
            curForce = self.coalitionsAndForce[curIndex]["force"]
            curTargets = mcuIcon.options['Targets']
            if curCoalition != 2: # remove duplicates: save only "2 --> 1"
                continue
            for target in curTargets:
                tarIndex = target
                tarMcuIcon = self.mcuIconsDict[tarIndex]
                tarCoalition = self.coalitionsAndForce[tarIndex]["coalition"]
                tarForce = self.coalitionsAndForce[tarIndex]["force"]
                if curCoalition == tarCoalition:
                    continue
                self.frontLineMcuIconPairs.append({"rigth": mcuIcon, "left": tarMcuIcon, "rightForce": curForce, "leftForce": tarForce})
                pairsCount += 1
        logging.debug(f"Front Line pairs prepared: {pairsCount} pairs")
        #logging.debug(f"======= BEGIN =====")
        #logging.debug(f"=====  2 --> 1  ===")
        #for pair in self.frontLineMcuIconPairs:
        #    logging.debug(f"  {pair['leftForce']}:{pair['left'].options['Index']} --> {pair['rigth'].options['Index']}:{pair['rightForce']}")
        #logging.debug(f"======= END =======")

    def calcFrontLine(self):
        self.frontLineMcuIconsArr = []
        self.frontLineMcuIconsDict = dict()
        nextIconId = self.startFrontLineId
        for pair in self.frontLineMcuIconPairs:
            leftMcuIcon = pair['left']
            rightMcuIcon = pair['rigth']
            leftForce = pair['leftForce']
            rightForce = pair['rightForce']

            x1 = float(leftMcuIcon.options["XPos"])
            y1 = float(leftMcuIcon.options["YPos"])
            z1 = float(leftMcuIcon.options["ZPos"])
            x2 = float(rightMcuIcon.options["XPos"])
            y2 = float(rightMcuIcon.options["YPos"])
            z2 = float(rightMcuIcon.options["ZPos"])

            #dist2d = math.sqrt(math.pow(x2-x1, 2)                      + math.pow(z2-z1, 2)) # sqrt(dx^2        + dz^2)
            #dist3d = math.sqrt(math.pow(x2-x1, 2) + math.pow(y2-y1, 2) + math.pow(z2-z1, 2)) # sqrt(dx^2 + dy^2 + dz^2)
            totalForce = leftForce + rightForce
            distFromLeft = (leftForce / totalForce)
            xF = x1 + (x2-x1)*distFromLeft
            #yF = y1 + (y2-y1)*distFromLeft
            zF = z1 + (z2-z1)*distFromLeft

            nextIconId += 1
            zMcuIcon = copy.deepcopy(leftMcuIcon)
            zMcuIcon.options["Index"] = nextIconId
            zMcuIcon.options["XPos"] = xF
            zMcuIcon.options["YPos"] = 0.00 # do not use yF, always 0
            zMcuIcon.options["ZPos"] = zF
            zMcuIcon.options["Coalitions"] = [1, 2]
            zMcuIcon.options["Conn_Targets"] = [leftMcuIcon.options["Index"], rightMcuIcon.options["Index"]]

            leftMcuIcon.options["FrontLine_Targets"] = leftMcuIcon.options.get("FrontLine_Targets",list()) + [zMcuIcon.options["Index"]]
            rightMcuIcon.options["FrontLine_Targets"] = rightMcuIcon.options.get("FrontLine_Targets",list()) + [zMcuIcon.options["Index"]]

            #logging.debug(f"  front {nextIconId}: ({x1},{y1},{z1}) -- ({xF},{yF},{zF}) -- ({x2},{y2},{z2})")
            self.frontLineMcuIconsArr.append(zMcuIcon)
            self.frontLineMcuIconsDict[nextIconId] = zMcuIcon
        logging.debug(f"Front Line generated up to {nextIconId} point")

    def calcDistance(self, p1, p2):
        dX = p2.options["XPos"] - p1.options["XPos"]
        dY = p2.options["YPos"] - p1.options["YPos"]
        dZ = p2.options["ZPos"] - p1.options["ZPos"]
        D = math.sqrt(math.pow(dX, 2) + math.pow(dY, 2) + math.pow(dZ, 2))
        return D

    def directFrontLine(self):
        # Clear targets
        for point in self.frontLineMcuIconsArr:
            point.options["Targets"] = []
            point.options["Rev_Targets"] = []
        # Calculate targets
        for point in self.frontLineMcuIconsArr:
            # FrontLine point always have 2 connections: to coalition "1" (red) and to coalition "2" (blue)
            redPoint = self.mcuIconsDict[point.options["Conn_Targets"][0]]
            bluePoint = self.mcuIconsDict[point.options["Conn_Targets"][1]]
            connectionsToRed = redPoint.options["FrontLine_Targets"]
            connectionsToBlue = bluePoint.options["FrontLine_Targets"]
            self.frontLineFromPoints(redPoint, connectionsToRed)
            self.frontLineFromPoints(bluePoint, connectionsToBlue)
            point.options["Conn_Hint"] = "r:{}, b:{}".format(connectionsToRed, connectionsToBlue) # debug
        # Join segments
        for point in self.frontLineMcuIconsArr:
            # Skip points with target
            if point.options["Targets"]:
                continue
            # Try to find target for other points
            possibleTargetPoints = []
            redPoint = self.mcuIconsDict[point.options["Conn_Targets"][0]]
            bluePoint = self.mcuIconsDict[point.options["Conn_Targets"][1]]
            levelOnePoints = redPoint.options["Targets"] + bluePoint.options["Targets"]
            for nearPointId in levelOnePoints:
                #logging.debug ("TEST-1 {}".format(nearPointId))
                nearPoint = self.mcuIconsDict[nearPointId]
                frontLinePoints = nearPoint.options.get("FrontLine_Targets",[])
                for frontLinePointId in frontLinePoints:
                    levelOneFrontLinePoint = self.frontLineMcuIconsDict[frontLinePointId]
                    if levelOneFrontLinePoint.options["Rev_Targets"]:
                        # This point already have connections
                        continue
                    if frontLinePointId == point.options["Index"]:
                        # This point same as source point
                        continue
                    if frontLinePointId in point.options["Rev_Targets"]:
                        # This connection creates loop of 2 points
                        continue
                    #logging.debug ("SELECT-2 {} -- {}".format(point.options["Index"], frontLinePointId))
                    possibleTargetPoints.append(levelOneFrontLinePoint)
            for targetPoint in possibleTargetPoints:
                point.options["Targets"].append(targetPoint.options["Index"])
                break # NOTE: take exactly one first item
        # Done
        logging.debug("Front Line direction updated with coalition info")

    def frontLineDirectVector(self, pointT, pointA, pointB):
        ax = pointA.options["XPos"]
        az = pointA.options["ZPos"]
        bx = pointB.options["XPos"]
        bz = pointB.options["ZPos"]
        tx = pointT.options["XPos"]
        tz = pointT.options["ZPos"]
        tc = pointT.options["Coalitions"][0]
        s = (bx-ax)*(tz-az)-(bz-az)*(tx-ax)
        if s > 0:
            return 1 if tc == 1 else -1
        elif s < 0:
            return -1 if tc == 1 else 1
        else:
            return 0

    def frontLineFromPoints(self, basePoint, points):
        # Check: at least 2 points
        if len(points) < 2:
            return

        # Interconnect all points
        for pointIdA in points:
            pointA = self.frontLineMcuIconsDict[pointIdA]
            minDist = None
            nearPoint = None
            for pointIdB in points:
                if pointIdA == pointIdB:
                    continue
                pointB = self.frontLineMcuIconsDict[pointIdB]
                d = self.calcDistance(pointA, pointB)
                if (minDist is None) or (d < minDist):
                    minDist = d
                    nearPoint = pointB

            if nearPoint:
                dir = self.frontLineDirectVector(basePoint, pointA, nearPoint)
                if dir < 0:
                    pointA.options["Targets"] = [nearPoint.options["Index"]]
                    nearPoint.options["Rev_Targets"] = [pointA.options["Index"]]
                else:
                    nearPoint.options["Targets"] = [pointA.options["Index"]]
                    pointA.options["Rev_Targets"] = [nearPoint.options["Index"]]

    def frontLineToString(self):
        self.frontLineString = "# Mission File Version = 1.0;\n"
        self.frontLineString += "\n"
        self.frontLineString += "Options\n"
        self.frontLineString += self.options.getRawData()
        for mcuIcon in self.frontLineMcuIconsArr:
            self.frontLineString += "\n"
            self.frontLineString += "MCU_Icon\n"
            self.frontLineString += "{\n"
            for optionName in mcuIcon.options:
                optionValue = mcuIcon.options[optionName]
                # Ignore option
                if optionName in self.ignoredOptions:
                    continue
                # Replace value for option
                if optionName in self.replacedOptions:
                    optionValue = self.replacedOptions[optionName]
                # Place option to string
                self.frontLineString += f"  {optionName} = {optionValue};\n"
            self.frontLineString += "}\n"
        self.frontLineString += "\n"
        self.frontLineString += "# end of file"

    def printFrontLineAsString(self):
        logging.debug(self.frontLineString)

    def saveFrontLineToFile(self, filePath):
        with open(filePath, "w") as f:
            f.write(self.frontLineString)
        logging.debug("Front Line saved to Mission file!")

    def calcVisual(self):
        self.visual.maxX = self.mcuIconsArr[0].x()
        self.visual.maxY = self.mcuIconsArr[0].y()
        self.visual.maxZ = self.mcuIconsArr[0].z()
        self.visual.minX = self.mcuIconsArr[0].x()
        self.visual.minY = self.mcuIconsArr[0].y()
        self.visual.minZ = self.mcuIconsArr[0].z()
        allMcuIcons = self.mcuIconsArr + self.frontLineMcuIconsArr
        for mcuIcon in allMcuIcons:
            if mcuIcon.x() > self.visual.maxX: self.visual.maxX = mcuIcon.x()
            if mcuIcon.y() > self.visual.maxY: self.visual.maxY = mcuIcon.y()
            if mcuIcon.z() > self.visual.maxZ: self.visual.maxZ = mcuIcon.z()
            if mcuIcon.x() < self.visual.minX: self.visual.minX = mcuIcon.x()
            if mcuIcon.y() < self.visual.minY: self.visual.minY = mcuIcon.y()
            if mcuIcon.z() < self.visual.minZ: self.visual.minZ = mcuIcon.z()
        dX = self.visual.maxX - self.visual.minX
        dY = self.visual.maxY - self.visual.minY
        dZ = self.visual.maxZ - self.visual.minZ

        kX = self.visual.imgH / dX
        kZ = self.visual.imgW / dZ
        self.visual.kX = min(kX, kZ)
        self.visual.kY = min(kX, kZ)
        self.visual.kZ = min(kX, kZ)

        ###############################################
        self.visual.kX = kX # make broken proportions #
        self.visual.kZ = kZ # make broken proportions #
        ###############################################

        logging.debug("Bounds calculated:")
        logging.debug(f"  x:  {self.visual.minX:10.3f} .. {self.visual.maxX:10.3f} -> {dX:10.3f}")
        logging.debug(f"  y:  {self.visual.minY:10.3f} .. {self.visual.maxY:10.3f} -> {dY:10.3f}")
        logging.debug(f"  z:  {self.visual.minZ:10.3f} .. {self.visual.maxZ:10.3f} -> {dZ:10.3f}")
        logging.debug(f"  kX: {self.visual.kX}")
        logging.debug(f"  kY: {self.visual.kY}")
        logging.debug(f"  kZ: {self.visual.kZ}")
        logging.debug(f"  ratio orig: {dZ/dX}")
        logging.debug(f"  ratio canv: {self.visual.imgW/self.visual.imgH}")


    def plotVisual(self):
        for mcuIcon in self.mcuIconsArr:
            self.visual.placePoint(mcuIcon)
        for mcuIcon in self.mcuIconsArr:
            curTargets = mcuIcon.options['Targets']
            for target in curTargets:
                tarMcuIcon = self.mcuIconsDict[target]
                self.visual.placeLine(mcuIcon, tarMcuIcon)
        for mcuIcon in self.frontLineMcuIconsArr:
            self.visual.placePoint(mcuIcon)
        for mcuIcon in self.frontLineMcuIconsArr:
            curTargets = mcuIcon.options['Targets']
            for target in curTargets:
                tarMcuIcon = self.frontLineMcuIconsDict[target]
                self.visual.placeLine(mcuIcon, tarMcuIcon, isFrontLine=True)
        for mcuIcon in self.mcuIconsArr + self.frontLineMcuIconsArr:
            self.visual.placeCaption(mcuIcon)

    def saveVisual(self, filePath):
        self.visual.saveToFile(filePath)
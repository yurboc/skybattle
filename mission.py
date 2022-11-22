import os
import json
import math
import copy

class Options:
    def __init__(self):
        self.rawData = ""

    def loadOptionsFromFile(self, filePath):
        self.rawData = ""
        linesCount = 0
        print(f"Load Options from file: {os.path.basename(filePath)}")
        with open(filePath, "r") as f:
            fileLines = f.readlines()
            foundOptions = False
            for line in fileLines:
                # Before "Options" block
                if not foundOptions and not line.startswith("Options"):
                    continue
                # Begin "Options" block
                if not foundOptions and line.startswith("Options"):
                    foundOptions = True
                    continue
                # Inside "Options" block
                if not line.startswith("}"):
                    self.rawData += line
                    linesCount += 1
                    continue
                # End of "Options" block
                if line.startswith("}"):
                    self.rawData += line
                    linesCount += 1
                    break
        print(f"Load Options done: {linesCount} lines")

    def printRawData(self):
        print(self.rawData)

    def getRawData(self):
        return self.rawData

    def hasData(self):
        return True if self.rawData else False

class MCU_Icon:
    def __init__(self, mcuIconStr=""):
        self.rawData = mcuIconStr
        self.options = dict()

    def loadFromString(self, mcuIconStr):
        self.rawData = mcuIconStr
        self.options = dict()

    def printRawData(self):
        print(self.rawData)

    def parse(self):
        #print(f"===== ITEM BEGIN =====")
        self.options = dict()
        for optionStr in self.rawData.splitlines(keepends=False):
            if "=" not in optionStr:
                continue
            optionStr = optionStr.replace(";", "")
            optionArr = optionStr.split(" = ")
            if len(optionArr) != 2:
                continue
            optionName = optionArr[0].strip()
            optionValue = optionArr[1].strip()
            optionValueObj = json.loads(optionValue)
            self.options[optionName] = optionValueObj
            #print(f"{optionName}:{optionValue}")
        #print(self.options)
        #print(f"===== ITEM END =====")

class Mission:
    def __init__(self):
        self.options = Options()
        self.mcuIconsArr = []
        self.mcuIconsDict = dict()
        self.coalitionsAndForce = dict()
        self.frontLineMcuIconPairs = []
        self.frontLineMcuIcons = []
        self.frontLineString = ""
    
    def loadMissionFromFile(self, filePath):
        # Load Options from file
        self.options.loadOptionsFromFile(filePath)

        # Load all MCU_Icon from file
        self.mcuIconsArr = []
        self.mcuIconsDict = dict()
        itemsCount = 0
        print(f"Load MCU_Icon items from file: {os.path.basename(filePath)}")
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
        print(f"Load MCU_Icon done: {itemsCount} items")

    def printMissionStat(self):
        print(f"===== BEGIN =====")
        print(f"Has Options    : {self.options.hasData()}")
        print(f"MCU_Icon count : {len(self.mcuIconsArr)} total, {len(self.mcuIconsDict)} unique")
        #print(f"==== OPTIONS ====")
        #self.options.printRawData()
        #print(f"=== MCU_ICONS ===")
        #self.mcuIcons[0].printRawData()
        print(f"====== END ======")

    def calcCoalitionAndForce(self):
        self.coalitionsAndForce = dict()
        for mcuIcon in self.mcuIconsArr:
            curIndex = int(mcuIcon.options['Index'])
            curCoalition = mcuIcon.options['Coalitions'][0]
            curForce = 50
            self.coalitionsAndForce[curIndex] = {"coalition": curCoalition, "force": curForce}
        print("Coalitions calculated!")

    def saveCoalitionForceJson(self, filePath):
        resJson = json.dumps(self.coalitionsAndForce, indent=2)
        with open(filePath, "w") as f:
            f.write(resJson)
        print("Coalitions saved to JSON!")

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
                self.frontLineMcuIconPairs.append({"left": mcuIcon, "rigth": tarMcuIcon, "leftForce": curForce, "rightForce": tarForce})
                pairsCount += 1
        print(f"Front Line pairs prepared: {pairsCount} pairs")
        #print(f"======= BEGIN =====")
        #print(f"=====  2 --> 1  ===")
        #for pair in self.frontLineMcuIconPairs:
        #    print(f"  {pair['leftForce']}:{pair['left'].options['Index']} --> {pair['rigth'].options['Index']}:{pair['rightForce']}")
        #print(f"======= END =======")

    def calcFrontLine(self):
        self.frontLineMcuIcons = []
        nextIconId = 1000
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
            yF = y1 + (y2-y1)*distFromLeft
            zF = z1 + (z2-z1)*distFromLeft

            nextIconId += 1
            zMcuIcon = copy.deepcopy(leftMcuIcon)
            zMcuIcon.options["Index"] = nextIconId
            zMcuIcon.options["XPos"] = xF
            zMcuIcon.options["YPos"] = yF
            zMcuIcon.options["ZPos"] = zF
            zMcuIcon.options["Coalitions"] = [1, 2]
            #print(f"  front {nextIconId}: ({x1},{y1},{z1}) -- ({xF},{yF},{zF}) -- ({x2},{y2},{z2})")
            self.frontLineMcuIcons.append(zMcuIcon)
        print(f"Front Line generated up to {nextIconId} point")

    def calcDistance(self, p1, p2):
        dX = p2.options["XPos"] - p1.options["XPos"]
        dY = p2.options["YPos"] - p1.options["YPos"]
        dZ = p2.options["ZPos"] - p1.options["ZPos"]
        D = math.sqrt(math.pow(dX, 2) + math.pow(dY, 2) + math.pow(dZ, 2))
        return D

    def directFrontLine(self):
        donePoints = []
        if len(self.frontLineMcuIcons) == 0:
            return
        
        firstPoint = self.frontLineMcuIcons[0]
        currentPoint = firstPoint
        self.frontLineMcuIcons.remove(currentPoint)
        donePoints.append(currentPoint)

        while self.frontLineMcuIcons:
            nextPoint = self.frontLineMcuIcons[0]
            minD = self.calcDistance(currentPoint, nextPoint)
            for point in self.frontLineMcuIcons:
                d = self.calcDistance(currentPoint, point)
                if d <= minD:
                    minD = d
                    nextPoint = point
            donePoints.append(nextPoint)
            self.frontLineMcuIcons.remove(nextPoint)
            currentPoint.options["Targets"] = [nextPoint.options["Index"]]
            currentPoint = nextPoint

        currentPoint.options["Targets"] = [firstPoint.options["Index"]]
        self.frontLineMcuIcons = donePoints
        print("Front Line directed")


    def frontLineToString(self):
        self.frontLineString = "# Mission File Version = 1.0;\n"
        self.frontLineString += "\n"
        self.frontLineString += "Options\n"
        self.frontLineString += self.options.getRawData()
        for mcuIcon in self.frontLineMcuIcons:
            self.frontLineString += "\n"
            self.frontLineString += "MCU_Icon\n"
            self.frontLineString += "{\n"
            for option in mcuIcon.options:
                self.frontLineString += f"  {option} = {mcuIcon.options[option]};\n"
            self.frontLineString += "}\n"
        self.frontLineString += "\n"
        self.frontLineString += "# end of file"

    def printFrontLineAsString(self):
        print(self.frontLineString)

    def saveFrontLineToFile(self, filePath):
        with open(filePath, "w") as f:
            f.write(self.frontLineString)
        print("Front Line saved to Mission file!")

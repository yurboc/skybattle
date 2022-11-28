import os
import json
import math
import copy


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
            self.frontLineMcuIconsArr.append(zMcuIcon)
            self.frontLineMcuIconsDict[nextIconId] = zMcuIcon
        print(f"Front Line generated up to {nextIconId} point")

    def calcDistance(self, p1, p2):
        dX = p2.options["XPos"] - p1.options["XPos"]
        dY = p2.options["YPos"] - p1.options["YPos"]
        dZ = p2.options["ZPos"] - p1.options["ZPos"]
        D = math.sqrt(math.pow(dX, 2) + math.pow(dY, 2) + math.pow(dZ, 2))
        return D

    def directFrontLine(self):
        donePoints = []
        totalD = 0
        if len(self.frontLineMcuIconsArr) == 0:
            return
        
        firstPoint = self.frontLineMcuIconsArr[0]
        currentPoint = firstPoint
        self.frontLineMcuIconsArr.remove(currentPoint)
        donePoints.append(currentPoint)

        while self.frontLineMcuIconsArr:
            nextPoint = self.frontLineMcuIconsArr[0]
            minD = self.calcDistance(currentPoint, nextPoint)
            for point in self.frontLineMcuIconsArr:
                d = self.calcDistance(currentPoint, point)
                if d <= minD:
                    minD = d
                    nextPoint = point
            totalD += d
            donePoints.append(nextPoint)
            self.frontLineMcuIconsArr.remove(nextPoint)
            currentPoint.options["Targets"] = [nextPoint.options["Index"]]
            currentPoint = nextPoint

        currentPoint.options["Targets"] = [firstPoint.options["Index"]]
        averageD = totalD / len(donePoints)

        # Remove too far Targets
        for point in donePoints:
            nextPoint = self.frontLineMcuIconsDict[point.options["Targets"][0]]
            d = self.calcDistance(point, nextPoint)
            if d > averageD * 2:
                point.options["Targets"] = []

        self.frontLineMcuIconsArr = donePoints
        print("Front Line directed")


    def frontLineToString(self):
        self.frontLineString = "# Mission File Version = 1.0;\n"
        self.frontLineString += "\n"
        self.frontLineString += "Options\n"
        self.frontLineString += self.options.getRawData()
        for mcuIcon in self.frontLineMcuIconsArr:
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

        kX = self.visual.imgW / dX
        kZ = self.visual.imgH / dZ
        self.visual.kX = min(kX, kZ)
        self.visual.kY = min(kX, kZ)
        self.visual.kZ = min(kX, kZ)

        ###############################################
        self.visual.kX = kX # make broken proportions #
        ###############################################

        print("Bounds calculated:")
        print(f"  x:  {self.visual.minX:10.3f} .. {self.visual.maxX:10.3f} -> {dX:10.3f}")
        print(f"  y:  {self.visual.minY:10.3f} .. {self.visual.maxY:10.3f} -> {dY:10.3f}")
        print(f"  z:  {self.visual.minZ:10.3f} .. {self.visual.maxZ:10.3f} -> {dZ:10.3f}")
        print(f"  kX: {self.visual.kX}")
        print(f"  kY: {self.visual.kY}")
        print(f"  kZ: {self.visual.kZ}")
        print(f"  ratio orig: {dZ/dY}")
        print(f"  ratio canv: {self.visual.imgW/self.visual.imgH}")


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

    def saveVisual(self, filePath):
        self.visual.saveToFile(filePath)
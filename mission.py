import os
import json

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
                self.frontLineMcuIconPairs.append({"left": mcuIcon, "rigth": tarMcuIcon, "leftForce": curForce, "rigthForce": tarForce})
                pairsCount += 1
        print(f"Front Line pairs prepared: {pairsCount} pairs")
        #print(f"======= BEGIN =====")
        #print(f"=====  2 --> 1  ===")
        #for pair in self.frontLineMcuIconPairs:
        #    print(f"  {pair['leftForce']}:{pair['left'].options['Index']} --> {pair['rigth'].options['Index']}:{pair['rigthForce']}")
        #print(f"======= END =======")
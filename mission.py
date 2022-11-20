import os

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

    def loadFromString(self, mcuIconStr):
        self.rawData = mcuIconStr

    def printRawData(self):
        print(self.rawData)

class Mission:
    def __init__(self):
        self.options = Options()
        self.mcuIcons = []
    
    def loadMissionFromFile(self, filePath):
        # Load Options from file
        self.options.loadOptionsFromFile(filePath)

        # Load all MCU_Icon from file
        self.mcuIcons = []
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
                    self.mcuIcons.append(MCU_Icon(currentMcuStr))
                    itemsCount += 1
                    currentMcuStr = ""
                    foundMCU = False
                    continue
        print(f"Load MCU_Icon done: {itemsCount} items")

    def printMissionStat(self):
        print(f"===== BEGIN =====")
        print(f"Has Options    : {self.options.hasData()}")
        print(f"MCU_Icon count : {len(self.mcuIcons)}")
        #print(f"==== OPTIONS ====")
        #self.options.printRawData()
        #print(f"=== MCU_ICONS ===")
        #self.mcuIcons[0].printRawData()
        print(f"====== END ======")
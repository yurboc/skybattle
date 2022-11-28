import json

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
    def x(self):
        return self.options['XPos']
    def y(self):
        return self.options['YPos']
    def z(self):
        return self.options['ZPos']

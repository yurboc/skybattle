import json
import logging

class MCU_Icon:
    def __init__(self, mcuIconStr=""):
        self.rawData = mcuIconStr
        self.options = dict()

    def loadFromString(self, mcuIconStr):
        self.rawData = mcuIconStr
        self.options = dict()

    def printRawData(self):
        logging.debug(self.rawData)

    def parse(self):
        #logging.debug(f"===== ITEM BEGIN =====")
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
            #logging.debug(f"{optionName}:{optionValue}")
        #logging.debug(self.options)
        #logging.debug(f"===== ITEM END =====")
    def x(self):
        return self.options['XPos']
    def y(self):
        return self.options['YPos']
    def z(self):
        return self.options['ZPos']

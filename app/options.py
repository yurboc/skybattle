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

    def getRawData(self):
        return self.rawData

    def hasData(self):
        return True if self.rawData else False

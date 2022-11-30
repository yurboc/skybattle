from PIL import Image, ImageDraw

class Vizualization:
    def __init__(self):
        self.minX = 0
        self.minY = 0
        self.minZ = 0
        self.maxX = 0
        self.maxY = 0
        self.maxZ = 0
        self.kX = 1 # X(picture) = X(orig) * kX
        self.kY = 1 # Y(picture) = Z(orig) * kY
        self.kZ = 1 # Z(picture) = Z(orig) * kZ
        self.imgW = 2048 # image X: 0..1023
        self.imgH = 768  # image Y: 0..767
        self.imgF = 10   # frame: 10 px: example for X: (0..9), 10..1033, (1034..1043)
        self.cnvW = self.imgW + 2 * self.imgF # canvas X: image + frame
        self.cnvH = self.imgH + 2 * self.imgF # canvas Y: image + frame
        self.imgX1 = self.imgF
        self.imgY1 = self.imgF
        self.imgX2 = self.imgX1 + self.imgW - 1
        self.imgY2 = self.imgY1 + self.imgH - 1

        self.pointR = 3 # point radius (R = D/2)
        self.pointW = 2 # point line width
        self.colorPointFill = {1: ((200, 150, 150, 0)), 2: ((150, 150, 200, 0))}
        self.colorPointLine = {1: ((200, 0, 0, 0)), 2: ((0, 0, 200, 0))}
        self.colorTargetLine = {1: ((255, 200, 200, 0)), 2: ((200, 200, 255, 0))}
        self.colorTargetLineDiff = (0, 200, 0, 0)
        self.colorTargetFrontLine = (200, 0, 200, 0)
        self.colorPointFrontFill = (255, 255, 200, 0)
        self.colorPointFrontLine = (200, 200, 100, 0)

        self.img = Image.new('RGB', (self.cnvW, self.cnvH), (230, 230, 230, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.draw.rectangle([(0, 0), (self.cnvW-1, self.imgY1)], (255, 255, 255, 0), (200, 200, 200, 0))
        self.draw.rectangle([(0, 0), (self.imgX1, self.cnvH-1)], (255, 255, 255, 0), (200, 200, 200, 0))
        self.draw.rectangle([(self.cnvW-1, self.cnvH-1), (self.imgX2+1, 0)], (255, 255, 255, 0), (200, 200, 200, 0))
        self.draw.rectangle([(self.cnvW-1, self.cnvH-1), (0, self.imgY2+1)], (255, 255, 255, 0), (200, 200, 200, 0))

    def mapMcuPointToImage(self, mcuPoint):
        y = (mcuPoint.x() - self.minX) * self.kX + self.imgF # map X_of_mcu_point to Y_of_image
        x = (mcuPoint.z() - self.minZ) * self.kZ + self.imgF # map Z_of_mcu_point to X_of_image
        return (int(x), int(y))

    def placePoint(self, mcuIcon):
        (x,y) = self.mapMcuPointToImage(mcuIcon)
        x1 = x-self.pointR
        y1 = y-self.pointR
        x2 = x+self.pointR
        y2 = y+self.pointR
        if len(mcuIcon.options['Coalitions']) == 1:
            self.draw.ellipse([(x1,y1),(x2,y2)], self.colorPointFill[mcuIcon.options['Coalitions'][0]], self.colorPointLine[mcuIcon.options['Coalitions'][0]])
        else:
            self.draw.ellipse([(x1,y1),(x2,y2)], self.colorPointFrontFill, self.colorPointFrontLine)

    def placeLine(self, mcuIcon1, mcuIcon2, isFrontLine=False):
        (x1,y1) = self.mapMcuPointToImage(mcuIcon1)
        (x2,y2) = self.mapMcuPointToImage(mcuIcon2)
        if isFrontLine:
            color = self.colorTargetFrontLine
            width = 3
        elif mcuIcon1.options['Coalitions'][0] == mcuIcon2.options['Coalitions'][0]:
            color = self.colorTargetLine[mcuIcon1.options['Coalitions'][0]]
            width = 1
        else:
            color = self.colorTargetLineDiff
            width = 1
        self.draw.line([(x1,y1),(x2,y2)], color, width)

    def saveToFile(self, filePath):
        self.img.save(filePath, "PNG")

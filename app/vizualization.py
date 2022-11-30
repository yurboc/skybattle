import math
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
        self.imgF = 20   # frame: for example 10 px: for X: (0..9), 10..1033, (1034..1043)
        self.cnvW = self.imgW + 2 * self.imgF # canvas X: image + frame
        self.cnvH = self.imgH + 2 * self.imgF # canvas Y: image + frame
        self.imgX1 = self.imgF
        self.imgY1 = self.imgF
        self.imgX2 = self.imgX1 + self.imgW - 1
        self.imgY2 = self.imgY1 + self.imgH - 1

        self.pointR = 3 # point radius (R = D/2)
        self.pointW = 2 # point line width
        self.arrowSize = 3 # arrow size on the Front Line (in pixels)
        self.colorPointFill = {1: ((200, 150, 150, 0)), 2: ((150, 150, 200, 0))}  # 1: light red, 2: light blue
        self.colorPointLine = {1: ((200, 0, 0, 0)), 2: ((0, 0, 200, 0))}          # 1: red, 2: blue
        self.colorTargetLine = {1: ((255, 200, 200, 0)), 2: ((200, 200, 255, 0))} # 1: light red, 2: light blue
        self.colorTargetLineDiff = (0, 200, 0, 0)      # green
        self.colorTargetFrontLine = (200, 0, 200, 0)   # magenta
        self.colorPointFrontFill = (255, 255, 200, 0)  # light yellow
        self.colorPointFrontLine = (200, 200, 100, 0)  # light yellow
        self.colorTextFrontLine = (0, 0, 0, 0)         # black

        self.img = Image.new('RGB', (self.cnvW, self.cnvH), (230, 230, 230, 0))
        self.draw = ImageDraw.Draw(self.img)
        self.draw.rectangle([(0, 0), (self.cnvW-1, self.imgY1)], (255, 255, 255, 0))
        self.draw.rectangle([(0, 0), (self.imgX1, self.cnvH-1)], (255, 255, 255, 0))
        self.draw.rectangle([(self.cnvW-1, self.cnvH-1), (self.imgX2+1, 0)], (255, 255, 255, 0))
        self.draw.rectangle([(self.cnvW-1, self.cnvH-1), (0, self.imgY2+1)], (255, 255, 255, 0))

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

    def arrowedLine(self, ptA, ptB, width=1, color=(0,255,0)):
        """ Draw line from ptA to ptB with arrowhead at ptB """
        """ https://stackoverflow.com/questions/63671018/how-can-i-draw-an-arrow-using-pil/63673261#63673261 """
        # Get drawing context
        draw = self.draw
        # Draw the line without arrows
        draw.line((ptA,ptB), width=width, fill=color)

        # Now work out the arrowhead
        # = it will be a triangle with one vertex at ptB
        # - it will start at 95% of the length of the line
        # - it will extend 3 pixels either side of the line
        x0, y0 = ptA
        x1, y1 = ptB
        # Now we can work out the x,y coordinates of the bottom of the arrowhead triangle
        xb = 0.95*(x1-x0)+x0
        yb = 0.95*(y1-y0)+y0

        # Work out the other two vertices of the triangle
        # Check if line is vertical
        if x0==x1:
            vtx0 = (xb-5, yb)
            vtx1 = (xb+5, yb)
        # Check if line is horizontal
        elif y0==y1:
            vtx0 = (xb, yb+5)
            vtx1 = (xb, yb-5)
        else:
            alpha = math.atan2(y1-y0,x1-x0)-90*math.pi/180
            a = self.arrowSize*math.cos(alpha)
            b = self.arrowSize*math.sin(alpha)
            vtx0 = (xb+a, yb+b)
            vtx1 = (xb-a, yb-b)

        #draw.point((xb,yb), fill=(255,0,0))    # DEBUG: draw point of base in red - comment out draw.polygon() below if using this line
        #im.save('DEBUG-base.png')              # DEBUG: save

        # Now draw the arrowhead triangle
        draw.polygon([vtx0, vtx1, ptB], fill=color)

    def placeCaption(self, mcuIcon):
        (x,y) = self.mapMcuPointToImage(mcuIcon)
        y -= 15
        if len(mcuIcon.options['Coalitions']) == 1: # Coalition point
            textColor = self.colorPointLine[mcuIcon.options['Coalitions'][0]]
        else: # Frontline point
            textColor = self.colorTextFrontLine
        self.draw.text((x,y), str(mcuIcon.options['Index']), fill=textColor, ancor="center")

    def placeLine(self, mcuIcon1, mcuIcon2, isFrontLine=False):
        ptStart = self.mapMcuPointToImage(mcuIcon1)
        ptStop = self.mapMcuPointToImage(mcuIcon2)
        if isFrontLine:
            color = self.colorTargetFrontLine
            width = 2
        elif mcuIcon1.options['Coalitions'][0] == mcuIcon2.options['Coalitions'][0]:
            color = self.colorTargetLine[mcuIcon1.options['Coalitions'][0]]
            width = 1
        else:
            color = self.colorTargetLineDiff
            width = 1
        if isFrontLine:
            self.arrowedLine(ptA=ptStart, ptB=ptStop, width=width, color=color) # with arrow
        else:
            self.draw.line([ptStart, ptStop], color, width) # without arrow

    def saveToFile(self, filePath):
        self.img.save(filePath, "PNG")

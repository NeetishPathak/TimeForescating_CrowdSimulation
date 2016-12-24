import time
import sys
import math
import random
from graphics import *
import csv
import operator

globalTime = 0
globalTick = 0
testSetting = 1
gridsOn = 0


minIncrement = 5
hourIncrement = 12

if testSetting == 1:
    settingspath = os.getcwd() + '/test1.txt'
    # settingspath = os.getcwd() + '/test1.txt'
    framepath = os.getcwd() + '/frame.txt'
    griDim = 25
    WIDTH = 1000
    HEIGHT = 600
    COORDS_X = 1000
    COORDS_Y = 600
else:
    settingspath = os.getcwd() + '/test2.txt'
    # settingspath = os.getcwd() + '/test1.txt'
    framepath = os.getcwd() + '/frame.txt'
    griDim = 5
    WIDTH = 400
    HEIGHT = 400
    COORDS_X = 40
    COORDS_Y = 40

class Grid:
    femtocells = []
    def __init__(self, width, height, nodeSize, nodeGap, window):
        self.opened = []
        self.closed = []
        self.width = width
        self.height = height
        self.nodeSize = nodeSize
        self.nodeGap = nodeGap
        self.window = window
        self.agent = []
        self.building = []
        self.triangle = []
        self.road = []
        self.obstacle = []
        self.polygon = []
        self.POI = []
        self.nodes = []
        self.start = ''
        self.end = ''
        self.blocks = []
        self.poiList = []
        self.srcDest = []
        self.routes = {}
        self.clock = Rectangle(Point(900,525),Point(900+50,525+50))
        self.timeString = "00:00"
        self.time = Text(self.clock.getCenter(),self.timeString)
        
    def flushRoutes(self):
        for x in self.routes:
            for p in x:
                self.blocks.remove(p)
    
    def markFemtocellRegion(self,poi):
        x = poi[0]/griDim
        y = poi[1]/griDim
        Grid.femtocells.append((x,y))
        Grid.femtocells.append((x-1,y-1))
        Grid.femtocells.append((x,y-1))
        Grid.femtocells.append((x+1,y-1))
        Grid.femtocells.append((x-1,y))
        Grid.femtocells.append((x+1,y))
        Grid.femtocells.append((x-1,y+1))
        Grid.femtocells.append((x,y+1))
        Grid.femtocells.append((x+1,y+1))
    
    def updateClock(self,val):
        global globalTick
        global globalTime
        if globalTick >= hourIncrement:
        #if globalTick >= 60:
            globalTime += 1
            globalTick = 0
        globalTime += val
#         if(globalTime >= 24):
#             globalTime = 0
        self.timeString = str(globalTime) + ":00"
        self.time.setText(self.timeString)
            
    def drawClock(self):
        self.clock.setFill("yellow")
        self.clock.draw(self.window)
        self.time.draw(self.window)
            
    def blockRiver(self):
        x1 = 28
        x2 = 31
        for j in range(0,24,3):
                
            for i in range(x1,x2): 
                self.blocks.append((i,j))
                self.blocks.append((i,j+1))
                self.blocks.append((i,j+2))
            x1 += 1
            if j > 3 and j < 9:
                x2 += 2
            else:
                x2 += 1
            self.blocks.append((28,4))
            self.blocks.append((28,3))
        
    def draw(self):
        for i in range(self.width):
            row = []
            for j in range(self.height):
#                 x = (i*self.nodeSize)+((i+1)*self.nodeGap)
#                 y = (j*self.nodeSize)+((j+1)*self.nodeGap)
                
                x = i*griDim
                y = j*griDim
                # color start/end/obstacle blocks differently
                if (i+1, j+1) == self.start:
                    color = "red"
                elif (i+1, j+1) == self.end:
                    color = "green"
                elif (i+1, j+1) in self.blocks:
                    color = "black"
                else:
                    color = "#636363"

                node = Node(x, y, self.nodeSize, self.window, color, i, j)
                row.append(node)
                node.draw()

            self.nodes.append(row)
        # draw all the nodes at once
        self.window.flush()
        self.load_env()

    def load_env(self):
        settings = open(settingspath)
        settings.readline()
        while True:
            line = settings.readline()
            if line=="":
                break;
            line = line.split()
            x = float(line[1])
            y = float(line[2])
            if line[0]=="poi":
                num = line[3]
                name = line[4]
                self.POI.append([[x,y,num,name]])
            if line[0]=="agent":
                rad = float(line[3])
                self.agent.append([[x,y,rad]])
            if line[0]=="obstacle":
                rad = float(line[3])
                type = str(line[4])
                self.obstacle.append([[x,y,rad, type]])
            if line[0]=="building":
                l = float(line[3])
                b = float(line[4])
                self.building.append([[x,y,l,b,line[5]]])
            if line[0]=="triangle":
                p2 = float(line[3])
                p3 = float(line[4])
                p4 = float(line[5])
                p5 = float(line[6])
                self.triangle.append([[x,y,p2,p3,p4,p5,line[6]]])
            if line[0] =="polygon":
                p2 = float(line[3])
                p3 = float(line[4])
                p4 = float(line[5])
                p5 = float(line[6])
                p6 = float(line[7])
                p7 = float(line[8])
                self.polygon.append([[x,y,p2,p3,p4,p5,p6,p7,line[9]]])
            if line[0]=="road":
                l = float(line[3])
                b = float(line[4])
                h = float(line[5])
                self.road.append([[x,y,l,b,h]])
        settings.close()
        self.draw_graphics()

    def draw_graphics(self):
        positions=[]

#         self.window.setCoords(0,0,480,480)
        for a in self.agent:
            x = a[0][0]
            y = a[0][1]
            z = a[0][2] - 0.1
            val = Circle( Point(x,y), z)
            val.setFill("red")
            positions.append([x,y])
            val.draw(self.window)
            a.append(val)
        
        for t in self.triangle:
            p1 = Point(t[0][0],t[0][1])
            p2 = Point(t[0][2],t[0][3])
            p3 = Point(t[0][4],t[0][5])
            poly = Polygon(p1,p2,p3)
            poly.setFill("#addd8e")
            poly.draw(self.window)
            t.append(poly)
        
        for p in self.polygon:
            p1 = Point(p[0][0],p[0][1])
            p2 = Point(p[0][2],p[0][3])
            p3 = Point(p[0][4],p[0][5])
            p4 = Point(p[0][6],p[0][7])
            
            
            cent_x = (p[0][0] + p[0][2] + p[0][4] + p[0][6])/4.0
            cent_y = (p[0][1] + p[0][3] + p[0][5] + p[0][7])/4.0
            poly = Polygon(p1,p2,p3,p4)
#             poly.setFill("#bf78ce")
            poly.setFill("gray")
            poly.draw(self.window)
            if p[0][8] == "River":
                self.blockRiver()
                poly.setFill("#99d8c9")
                
            text = Text(Point(cent_x,cent_y),p[0][8])
            text.setSize(8)
            text.draw(self.window)
            p.append(poly)
        
        for a in self.building:
#             x = a[0][0] * 10 + a[0][0] * self.nodeGap
#             y = a[0][1] * 10 + a[0][1] * self.nodeGap
#             z = a[0][3] * 10 + a[0][3] * self.nodeGap
#             w = a[0][2] * 10 + a[0][2] * self.nodeGap
            if(a[0][4] != "Street"):
                p1 = int(a[0][0]/griDim) 
                p2 = int(a[0][1]/griDim) 
    #             self.blocks.append((p1,p2))
                l = a[0][3]
                h = a[0][2]
#                 print p1, p2
#                 print l, h
                itr1 = 0
                while(l>=griDim):
    #                 self.blocks.append((p1+itr1,p2))
                    itr2 = 0
                    h = a[0][2]
                    while(h>=griDim):
    #                     if (p1+itr1,p2+itr2) not in self.poiList:
                        if(a[0][4] != "Bridge"):
                            self.blocks.append((p1+itr1,p2+itr2))
    #                         print "blocking ", p1+itr1,p2+itr2
    #                         print "l,h ",l,h
                        else:
                            if (p1+itr1,p2+itr2) in self.blocks:
                                self.blocks.remove((p1+itr1,p2+itr2))
                        itr2 += 1
                        h -=griDim
                    itr1 += 1
                    l -= griDim
                    
            bd1 = Point(a[0][0], a[0][1])
#           bd2 = Point(a[0][0], a[0][1] + a[0][2])
            bd3 = Point(a[0][0] + a[0][3], a[0][1] + a[0][2])
            
#             bd1 = Point(x, y)
    #         bd2 = Point(a[0][0], a[0][1] + a[0][2])
#             bd3 = Point(x + z, y + w)
    #         bd4 = Point(a[0][0] + a[0][3], a[0][1])

            #Line(bd1,bd2).draw(window)
            #Line(bd2,bd3).draw(window)
            #Line(bd3,bd4).draw(window)
            #Line(bd4,bd1).draw(window)
            
            rect = Rectangle(bd1,bd3)
            if "College" == str(a[0][4]):
                color = '#fdae6b'
            elif 'Hospital' == str(a[0][4]):
                color = 'Blue'
            elif "Forest" == str(a[0][4]):
                color = "Green"
            elif "Pub" == str(a[0][4]):
                color = "Yellow"
            elif "Home" == str(a[0][4]):
                color = "White"
            elif "Office" == str(a[0][4]):
                color = "Magenta"
            elif "Gym" == str(a[0][4]):
                color = "Maroon"
            elif "Pool" == str(a[0][4]):
                color = "cyan"
            elif "Park" == str(a[0][4]):
                color = "Green"
            elif "Hostel" == str(a[0][4]):
                color = "Yellow"
            elif "Bridge" == str(a[0][4]):
                color = "Brown"
            elif "Mall" == str(a[0][4]):
                color = "#5ab4ac"
            elif "Restaurant" == str(a[0][4]):
                color = "#d8b365"
            else:
                color = "#addd8e"
            rect.setFill(color)
            rect.draw(self.window)
            anchorPoint = rect.getCenter()
            text = Text(anchorPoint, a[0][4])
            text.setSize(8)
            text.draw(self.window)
            a.append(rect)
    #     time.sleep(10)

        for r in self.road:
            r1= Point(r[0][0],r[0][1])
            r2 = Point(r[0][0] + r[0][3],r[0][1]+r[0][2])
            rd = Rectangle(r1,r2)
            rd.setFill("#636363")
            rd.setOutline("#636363")
            rd.draw(self.window)
            r.append(rd)

        for o in self.obstacle:
            val = Circle( Point(o[0][0],o[0][1]), o[0][2])
            type = o[0][3]
            if type == "road":
                val.setFill("#636363")
                val.setOutline("#636363")
            else:
                val.setFill("black")
            val.draw(self.window)
            o.append(val)
            
        for poi in self.POI:
#             x = poi[0][0] * 10 + poi[0][0] * self.nodeGap
#             y = poi[0][1] * 10 + poi[0][1] * self.nodeGap
            poi1 = Point(poi[0][0], poi[0][1])
            poi2 = Point(poi[0][0] + griDim, poi[0][1] + griDim)
#             poi1 = Point(x,y)
#             poi2 = Point(x + self.nodeSize, y + self.nodeSize)
            '''If point is a point of interest, then it should not be blocked'''
            self.poiList.append((poi[0][0],poi[0][1]))
            
            rct_poi = Rectangle(poi1,poi2)
            if int(poi[0][2]) <= 31:
                rct_poi.setFill("Red")
                rct_poi.draw(self.window)
                text = Text(rct_poi.getCenter(),poi[0][2])
                self.srcDest.append(poi[0])
            else:
                rct_poi.setFill("#e0ecf4")
                rct_poi.draw(self.window)
                text = Text(rct_poi.getCenter(),poi[0][3])
                self.markFemtocellRegion(poi[0])
            text.setSize(8)
            text.draw(self.window)
#         print self.blocks   
        
        matrix = []
        for i in range(0,COORDS_X,griDim):
            m1 = []
            for j in range(0,COORDS_Y,griDim):
                x = i
                y = j
                m1.append((x*(COORDS_X/griDim) + y)/griDim)
                
                if gridsOn == 1:
                    rP = Rectangle(Point(x,y),Point(x + griDim,y + griDim))
                    rP.setOutline("white")
                    rP.draw(self.window)
                    t = Text(rP.getCenter(),(i*(COORDS_X/griDim) + j)/griDim)
                    t.setSize(8)
                    t.draw(self.window)
            matrix.append(m1)

    def AlternatePath(self,path):
        startNode = self.nodes[self.start[0]-1][self.start[1]-1]
        endNode = self.nodes[self.end[0]-1][self.end[1]-1]

        self.opened = []
        self.closed = []
        # add the start node to the opened list so the loop can start
        self.opened.append(startNode)

        # set the gScore of the start node to 0 because it is 0 units away from start
        startNode.setGScore(0)

        # fScore = gScore + hCost but gScore = 0 for first node therefore fScore = hCost = distance from start to end
        startNode.setFScore(self.getDistance(startNode, endNode))
        
        for cord in path:
            self.blocks.append((cord[0],cord[1]))

        #print self.blocks
            
        while self.opened:
            # current is an opened node with the lowest fScore
            current = self.opened[0]

            for node in self.opened:
                if node.fScore < current.fScore:
                    current = node

            if current == endNode:
                # found the path - display the path
                path1 = []
                node = endNode
                
                while node.getParent():
                    data = (node.getParent().row,node.getParent().column)
                    path1.append(data)
                    node = node.getParent()
                #path.pop()
#                 print path1
                self.reconstructPath(endNode)

                for cord in path:
                    self.blocks.remove((cord[0],cord[1]))
            
                return(True)

            self.opened.remove(current)
            self.closed.append(current)

            for neighbour in self.getNeighbours(current):
                if neighbour in self.closed:
                    continue    # ignore it because it has already been evaluated

                # the distance from start to a neighbour
                tempGScore = current.gScore + self.getDistance(current, neighbour)
                if neighbour not in self.opened:    # discover a new node
                    self.opened.append(neighbour)
                elif tempGScore >= neighbour.gScore:
                    continue    # this is not a better path

                # this path is the best path until now
                neighbour.setParent(current)
                neighbour.setGScore(tempGScore)
                neighbour.setFScore(tempGScore + self.getDistance(neighbour, endNode)) # fScore = gScore + hCost
            
        return False

    #Given a start and end point on the grid, this function calculates all the best paths between them.
    #All the neighbours of the node on the grid are examined and least cost path is selected.
    #Once a path is selected, all the nodes of that path are blocked and the function is called recursively
    #to find a another possible path. Once found, the nodes are unblocked again.
    def findPath(self,start,end,path):
        self.start = start
        self.end = end
#         startNode = self.nodes[self.start[0]-1][self.start[1]-1]
#         endNode = self.nodes[self.end[0]-1][self.end[1]-1]
        startNode = self.nodes[self.start[0]][self.start[1]]
        endNode = self.nodes[self.end[0]][self.end[1]]

        self.opened = []
        self.closed = []

        #for cord in path:
        #    self.blocks.append((cord[0],cord[1]))

        # add the start node to the opened list so the loop can start
        self.opened.append(startNode)

        # set the gScore of the start node to 0 because it is 0 units away from start
        startNode.setGScore(0)

        # fScore = gScore + hCost but gScore = 0 for first node therefore fScore = hCost = distance from start to end
        startNode.setFScore(self.getDistance(startNode, endNode))
        while self.opened:
            # current is an opened node with the lowest fScore
            current = self.opened[0]

            for node in self.opened:
                if node.fScore < current.fScore:
                    current = node
            if current == endNode:
                # found the path - display the path
                path = []
                node = endNode
                #print "Code gets stuck in following while loop"
                while node.getParent():
                    #print node.getParent()
                    data = (node.getParent().row,node.getParent().column)
                    #print node.getParent().row,node.getParent().column
                    path.append(data)
                    node = node.getParent()
                #path.pop()
                #print path
                
                pathtimes = self.reconstructPath(endNode)
                if (start,end) not in self.routes.keys():
                    self.routes[(start,end)] = []
                    self.routes[(start,end)].append([pathtimes])
                
                else:
                    self.routes[(start,end)].append([pathtimes])
                
                #print self.AlternatePath(path)
#                 print self.findPath(self.start,self.end,path)
                #self.findPath(self.start,self.end,path)
                #for cord in path:
                #    if (cord[0],cord[1]) in self.blocks:
                #        self.blocks.remove((cord[0],cord[1]))
                '''
                for node in self.closed:
                    node.parent = None
                current.parent = None
                endNode.parent = None
                '''
                self.resetNodes()
                return(True)

            self.opened.remove(current)
            self.closed.append(current)

            for neighbour in self.getNeighbours(current):
                if neighbour in self.closed:
                    continue    # ignore it because it has already been evaluated

                # the distance from start to a neighbour
                tempGScore = current.gScore + self.getDistance(current, neighbour)
                if neighbour not in self.opened:    # discover a new node
                    self.opened.append(neighbour)
                elif tempGScore >= neighbour.gScore:
                    continue    # this is not a better path

                # this path is the best path until now
                neighbour.setParent(current)
                neighbour.setGScore(tempGScore)
                neighbour.setFScore(tempGScore + self.getDistance(neighbour, endNode)) # fScore = gScore + hCost

        self.resetNodes()
        return False    # failure to find a path

    def resetNodes(self):
        for row in self.nodes:
            for node in row:
                node.parent = None
                node.fScore = sys.maxsize
                node.gScore = sys.maxsize
        
    def getDistance(self, node, endNode):
        xDistance = node.column - endNode.column
        yDistance = node.row - endNode.row

        hCost = math.sqrt((xDistance**2) + (yDistance**2))

        return(hCost)

    def getNeighbours(self, node):
        neighbours = []
        row = node.row
        column = node.column
        # add corners if the path can go diagonally
        #adjacentCoordinates = [(row-1, column), (row, column-1), (row, column+1), (row+1, column)]
        adjacentCoordinates = [(row-1, column), (row, column-1), (row, column+1), (row+1, column), (row-1, column-1), (row-1, column+1), (row+1, column-1), (row+1, column+1)]

        for coord in adjacentCoordinates:
            if (coord[0], coord[1]) not in self.blocks and coord[0] >= 0 and coord[0] <= self.width-1 and coord[1] >= 0 and coord[1] <= self.height-1:
                # valid node
                neighbours.append(self.nodes[coord[0]][coord[1]])

        return(neighbours)

    def reconstructPath(self, endNode):
        global globalTime
        global globalTick
        if (globalTime >= 24):
            return
        path = []
        
        self.updateClock(0)
        endNode.changeColor("green")
        current = endNode.getParent()
        data = (endNode.row,endNode.column,self.getTime(),self.isFemtoCell(endNode.row,endNode.column))
        path.append(data)
        
        
        globalTick += 1
        self.updateClock(0)
        data = (current.row,current.column,self.getTime(),self.isFemtoCell(current.row,current.column))
        path.append(data)
        
        while current.getParent() and globalTime < 24:
            #current.changeColor("black")
            
            globalTick += 1
            self.updateClock(0)
            data = (current.getParent().row,current.getParent().column,self.getTime(),self.isFemtoCell(current.getParent().row,current.getParent().column))
#             time.sleep(0.005)
            self.window.flush()
            current = current.getParent()
            path.append(data)

        #data = (current.row,current.column,self.getTime(),self.isFemtoCell(current.row, current.column))
        #path.append(data)
        globalTick += 1
        current.changeColor("blue")
        self.window.flush()
        return path
    
    def isFemtoCell(self,row,col):
        if (row,col) in Grid.femtocells :
            index = Grid.femtocells.index((row,col))
            femtoNo = ((int)(index/9) + 1)
            return femtoNo
        return 0
        
    def getTime(self):
        global globalTick
        global globalTime

        minutes = globalTick * minIncrement
        #minutes = globalTick
        return str(globalTime) + ':' + str(minutes)
        
    def showBlocked(self):
        for m in self.blocks:
            color = "black"
            node = Node(m[0]*griDim, m[1]*griDim, griDim, self.window, color, m[0], m[1])
            node.draw()
            
    def showFemtocellRegions(self):
        for f in self.femtocells:
            color = "#e0ecf4"
            node = Node(f[0]*griDim, f[1]*griDim, griDim, self.window, color, f[0], f[1])
            node.draw()

class Node:
    def __init__(self, x, y, size, window, color, row, column):
        self.x = x
        self.y = y
        self.size = size
        self.window = window
        self.color = color
        self.row = row
        self.column = column
        self.parent = None
        self.fScore = sys.maxsize
        self.gScore = sys.maxsize

    def draw(self):
        node = Rectangle(Point(self.x, self.y), Point(self.x + self.size, self.y + self.size))
#         node = Circle(Point(self.x, self.y),0.4)
        node.setFill(self.color)
        node.setOutline(self.color)
        node.draw(self.window)

    def setFScore(self, fScore):
        self.fScore = fScore

    def setGScore(self, gScore):
        self.gScore = gScore

    def setParent(self, parent):
        self.parent = parent

    def getParent(self):
        return(self.parent)

    def changeColor(self, newColor):
        xC = self.x/griDim
        yC = self.y/griDim
        nodeFlash = Rectangle(Point(self.x, self.y), Point(self.x + self.size, self.y + self.size))
        if((xC,yC) in Grid.femtocells):
            nodeFlash.setFill("#ccff00")
            nodeFlash.draw(self.window)
        node = Circle(Point((2*self.x + self.size)/2, (2*self.y + self.size)/2),3.0)
        
        node.setFill(newColor)
        node.setOutline(newColor)
        node.draw(self.window)
        #time.sleep(0.0001)
        node.undraw()
        nodeFlash.undraw()
        
def generateRandom():
    return random.randint(0,30)

def expoStochasticVar(iat):
    
    rndm = random.random()
    nxtTime = ((-1) * math.log(rndm))*(iat)
    #a = "%.2f" % nxtTime
    return round(nxtTime,2)


def main():
	global globalTime
	global globalTick
	# size in terms of # of nodes
	gridWidth = WIDTH
	gridHeight = HEIGHT


	# size of each node in pixels
	nodeSize = 10
	# gap between each node in pixels
	gap = 2
	# subtracting 5px just makes it look nicer
	screenWidth = (gridWidth * nodeSize) 
	screenHeight = (gridHeight * nodeSize) + ((gridHeight ) * gap) 

	# create window
	window = GraphWin("A* Simulation", WIDTH, HEIGHT, autoflush=False)
	window.setBackground("#636363")
	window.setCoords(0,0,COORDS_X,COORDS_Y)
	#     window.flush()

	grid = Grid(COORDS_X/griDim, COORDS_Y/griDim, griDim, gap, window)
	grid.draw()

	#Simulating pedestrians movement

	#     if grid.findPath((16,13),(1,1),[]):
	#     if grid.findPath((20,1),(28,18),[]):
	#     if grid.findPath((4,21),(24,1),[]):
	#     if grid.findPath((31,1),(38,10),[]):

	#print grid.srcDest
	grid.drawClock()
	out = open('routes.csv','wb')
	writer = csv.writer(out, delimiter=',')
	data = [['Day','Simulation','Time','Minutes','xpos','ypos','FemtoCell']]
	writer.writerows(data)

	if 1:
		days = 1
		while days <= 15:
			pedestrians = 100
			while pedestrians > 0:
				while globalTime < 24: 
					a = generateRandom()
					b = generateRandom()
					
					while(b == a):
						b = generateRandom()
					#print a,b
					
					st = (int(grid.srcDest[a][0]/griDim),int(grid.srcDest[a][1]/griDim))
					ds = (int(grid.srcDest[b][0]/griDim), int(grid.srcDest[b][1]/griDim))
					#print st, ds
					if grid.findPath(st,ds,[]):
							#print("Path Successful")
						pass
							 
					else:
						#print "Path Not Found " + str(st) + ' ' + str(ds)
						#print globalTime
						window.flush()
				globalTime = 0
				globalTick = 0
				for keys in grid.routes.keys():
					for route in grid.routes[keys]:
						for y in route:
							for x in y:
								#out.write(str(pedestrians) + ' ' + str(x[2]) + ' ' + str(x[0]) + ' ' +str(x[1]) + '\n')
								timeParts = str(x[2]).split(":")
								#print timeParts
								if int(timeParts[0]) >= 24:
									continue
								mins = int(timeParts[0])*60 + int(timeParts[1])
								data = [[str(days),str(pedestrians),str(x[2]),mins,str(x[0]),str(x[1]),str(x[3])]]
								writer.writerows(data)
				grid.routes.clear()
				pedestrians -= 1
				print pedestrians
			days += 1
	else:
		#if grid.findPath((3,20),(37,10),[]):
		if grid.findPath((0, 0),(26, 18),[]):
			print("Path Successful")
		else:
			print("Path Not Found")
			for row in grid.nodes:
				for node in row:
					node.changeColor("red")
	out.close()
	window.getMouse();

main()

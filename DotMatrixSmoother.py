#import numpy as np
import math
import PIL
from scipy.spatial import Delaunay
import numpy as np

#import Matplotlib as mpl

#vars:
sizeMatrix = 35
valueDefaultMatrix = 3

#code:

##
Dots = [[valueDefaultMatrix for x in range(sizeMatrix)] for y in range(sizeMatrix)] 

def Col(value: int):
    
    if value == -1:
        return "\033[0m"
    elif value >= 0 and value <=255:
        return f"\033[48;5;{value}m"
    

def DysplayDots(dots):
    m = 1
    for y in dots:
        for x in y:
            if x != None and x > m: m = x
        
            
    print(m)
    if m != 0: m = 23/m
    #print(m*valueDefaultMatrix, Col(round(m*valueDefaultMatrix))+' ')
    for iy, y in enumerate(dots):
        for ix, dot in enumerate(y):
            #print([ix, iy])
            if dot != None:
                if [ix, iy] in [[p[0], p[1]] for p in setPoints]:
                    #print(round(dot*m+232))
                    print(Col(round(dot*m)+232) +str(round(dot)), end = ' ' + Col(-1))
                    continue
                print(Col(round(dot*m)+232) +' ', end = ' ' + Col(-1))
        for _ in range(len(str(valueDefaultMatrix))//3):
            print()
        print()
    print(m, int(m**-1*23))
    for x in range(int(m**-1*23)+1):
        print(Col(int(x*m+232))+str(x), end=Col(-1)+' ')

def areaTriangle(dots):#[[x, y][x, y][x, y]]
    #print(dots)
    return abs(dots[0][0]*(dots[1][1]-dots[2][1]) + dots[1][0]*(dots[2][1]-dots[0][1]) + dots[2][0]*(dots[0][1]-dots[1][1]))

def insideTriangle(dots, checkpoint):#[[y, x][y, x][y, x]] - [y, x]
    S = [areaTriangle([dots[0], checkpoint, dots[1]]), areaTriangle([dots[1], checkpoint, dots[2]]), areaTriangle([dots[0], checkpoint, dots[2]])]
    triS = areaTriangle(dots)
    return (True if sum(S) == triS else False)   
    
    
def findTriangles(dots):
    l = len(dots)
    triOut = []
    for i1 in range(l):
        for i2 in range(i1+1, l):
            for i3 in range(i2+1, l):
                tri = np.array([dots[i1], dots[i2], dots[i3]])
                #print(tri)
                inside = [(insideTriangle(tri, check) if check not in tri else False) for check in dots]
                #print(inside)
                if True not in inside:
                    triOut.append([dots[i1], dots[i2], dots[i3]])
    return triOut
def ravioliFindTriangles(points):
    tri = Delaunay(points)
    triangles = points[tri.simplices]
    return triangles




#x, y, z
#A###B##
########
#D###C## operation order --> A, B, C, D                                                jjj
setPoints = [[-3, 3, 10], [2, 1, 0], [3, -2, 0], [-1, -3, 0], [1, -1, 0], [-2, 2, 2], [0, 0, 5]]
c = 5.5
for i1, x in enumerate(setPoints):
    for i2 in range(2):

        setPoints[i1][i2]= int(x[i2]*c+sizeMatrix/2)
    Dots[x[1]][x[0]] = x[2]
  
#accepts a list of points [[x1, y1], [x2, y2]...]  <--- this is for when u get confused an hour after writing this code <--- this is for when u dont know what to do
def TestRun(points:list):
    out = []
    for p in points:
        d = []
        for i in range(len(setPoints)):
            d.append(math.sqrt((p[0]-setPoints[i][0])**2+(p[1]-setPoints[i][1])**2))
        #print(d)
        #check if point is inside quad
        if True:
            w = []
            k = []
            for i1 in range(len(setPoints)):
                if d[i1] != 0:
                    w.append(1/d[i1])
                    k.append(w[i1]*setPoints[i1][2])
                    
                else: 
                    out.append(-1)
                    return out
            out.append(sum(k)/sum(w))
    return out
def TestRunTri(triPoints, pixel):
    out = []
    if pixel not in [[p[0], p[1]] for p in setPoints]:
        for tri in triPoints:
            #print('fff', tri, pixel)
            if insideTriangle(tri, pixel):
                d = []
                for i in range(len(tri)):
                    d.append(math.sqrt((pixel[0]-tri[i][0])**2+(pixel[1]-tri[i][1])**2))
                #print('im alive')
                #check if point is inside quad

                w = []
                k = []
                for i1 in range(len(tri)):
                    if d[i1] != 0:
                        w.append(1/d[i1])
                        #print(w, tri, i1)
                        k.append(w[len(w)-1]*tri[i1][2])
                        #print(k)
                        out.append(sum(k)/sum(w))
        if len(out) != 0:
        
            return sum(out)/len(out)
    else:
        return setPoints[[[p[0], p[1]] for p in setPoints].index(pixel)][2]
    #except Exception as e:
    #    print(f'{e}\n\n{triPoints}\n\n{pixel}\n\n{out}')
    #    exit()
    #
print(setPoints)
for y, _ in enumerate(Dots):
    for x in range(len(_)):
        a = TestRun([[x, y]])[0]
        if a != -1:
            Dots[y][x] = a


print(insideTriangle([setPoints[0], setPoints[1], setPoints[6]], setPoints[5]))
#print(findTriangles(np.array(setPoints)))
#DysplayDots(Dots)
#t = findTriangles(setPoints)
t = ravioliFindTriangles(np.array(setPoints))
for x in t:
    print(x)
print(len(t))
for i1, y in enumerate(Dots):
    for i2, x in enumerate(y):
        Dots[i1][i2] = TestRunTri(t, [i2, i1])

DysplayDots(Dots)
for i1, y in enumerate(Dots):
    for i2, x in enumerate(y):
        Dots[i1][i2] = TestRun([[i2, i1]])[0]
#TestRun(setPoints)
DysplayDots(Dots)

#find every triangle
#

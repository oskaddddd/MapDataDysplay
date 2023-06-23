import numpy as np
import math
import PIL

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
    m = 0
    for y in dots:
        
        if max(y) > m: m = max(y)
    print(m)
    if m != 0: m = 23/m
    #print(m*valueDefaultMatrix, Col(round(m*valueDefaultMatrix))+' ')
    for iy, y in enumerate(dots):
        for ix, dot in enumerate(y):
            #print([ix, iy])
            if [ix, iy] in [[p[0], p[1]] for p in setPoints]:
                #print('adasdadadada')
                print(Col(round(dot*m+232)) +str(dot), end = ' ' + Col(-1))
                continue
            print(Col(round(dot*m+232)) +' ', end = ' ' + Col(-1))
        for _ in range(len(str(valueDefaultMatrix))//3):
            print()
        print()
    print(m, int(m**-1*23))
    for x in range(int(m**-1*23)+1):
        print(Col(int(x*m+232))+str(x), end=Col(-1)+' ')

def areaTriangle(dots):#[[x, y][x, y][x, y]]
    return abs(dots[0][0]*(dots[1][1]-dots[2][1]) + dots[1][0]*(dots[2][1]-dots[0][1]) + dots[2][0]*(dots[0][1]-dots[1][1]))
        
        
def findTriangles(dots):

        
#x, y, z
#A###B##
########
#D###C## operation order --> A, B, C, D
setPoints = [[-3, 3, 10], [2, 1, 0], [3, -2, 8], [3, -2, 8],[3, -2, 8],[3, -2, 8], [-1, -3, 0], [1, -1, 0], [-2, 2, 2], [0, 0, 5]]
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

print(setPoints)
for y, _ in enumerate(Dots):
    for x in range(len(_)):
        a = TestRun([[x, y]])[0]
        if a != -1:
            Dots[y][x] = a
        
DysplayDots(Dots)
print(findTriangles(np.array(setPoints)))


#find every triangle
#

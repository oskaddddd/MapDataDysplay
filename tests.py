import DotMatrixSmoother as dms
import numpy as np
#vars:
sizeMatrix = 35
valueDefaultMatrix = 3

#code:

##
Dots = [[valueDefaultMatrix for x in range(sizeMatrix)] for y in range(sizeMatrix)] 
setPoints = [ [2, 1, 1], [3, -2, 8], [-1, -2, 0], [-2, 2, 2], [0, 0, 9], [-3, -3, 7], [3, 0, 2], [3, 3, 0], [-3, 3, 0],[3, -3, 0]]

c = 5.5
for i1, x in enumerate(setPoints):
    for i2 in range(2):

        setPoints[i1][i2]= int(x[i2]*c+sizeMatrix/2)
    Dots[x[1]][x[0]] = x[2]
t = dms.ravioliFindTriangles(np.array(setPoints), False)
for i1, y in enumerate(Dots):
    for i2, x in enumerate(y):
        Dots[i1][i2] = dms.TestRunTri(t, [i2, i1], True, setPoints=setPoints)
#print(Dots)
dms.DysplayDots(Dots, setPoints)

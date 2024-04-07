import pyopencl as cl
import numpy as np
from scipy.spatial import Delaunay
import math
import os
import PIL.Image

from Gradient import gradient
import ReadSettings

os.environ['PYOPENCL_NO_CACHE'] = '1'



class interpolate_delauny_gpu():
    def __init__(self, points:np.ndarray, mask:PIL.Image.Image, maxMin:tuple, gradientInfo, clip = True, interactive = False):
        #Seperate the values of the points from said points
        self.pointValues = points[:, 2]
        self.points = points[:, :2]

        self.gradientInfo = gradientInfo
        
        #Determine the maximum and minimum value of the points
        self.minVal = maxMin[0]
        self.maxVal = maxMin[1]
        
        self.maxMin = np.array(maxMin, dtype=np.int32)
            

        #Determines what shade of color will a value be
        self.valueImpact = (self.maxVal-self.minVal)/255

        #Create other class values
        self.mask = mask
        self.clip = clip
        self.resolution = mask.size

        self.mask = np.array(self.mask)
        
        #Opencl stuff
        self.ctx = cl.create_some_context(interactive=interactive)
        self.queue = cl.CommandQueue(self.ctx)
        self.mf = cl.mem_flags

         
    def CreateBuffers(self, showTriangles = False):
        
        #Create the points array seperated from values
        p = points[:, 2]
        points = points[:, :2]
        
        #Calculate the triangles
        tri = Delaunay(points)
        
        #Convert the triangles to a usable format
        triangles = np.empty((tri.simplices.shape[0], 3, 3), dtype=np.int32)
        for i, simplex in enumerate(tri.simplices):
            triangle = [np.array([points[index][0], points[index][1], p[index]]) for index in simplex]
            self.triangles[i] = triangle
        
        #Create the triangle buffer and copy the data to it
        self.triBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = triangles.nbytes)
        cl.enqueue_copy(self.queue, self.triBuffer, triangles)
        
        
        #Create the mask buffer and copy the data to it
        self.imageBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = self.mask.nbytes)
        cl.enqueue_copy(self.queue, self.imageBuffer, self.mask)
        
        
        #Create the buffers for max and min values
        self.maxMinBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = self.maxMin.nbytes)
        cl.enqueue_copy(self.queue, self.maxMinBuffer, self.maxMin)
        
        
        #Create the gradient info buffer
        gradientInfoFlat = np.zeros((len(self.gradientInfo), 4), dtype=np.float32)
        for i in range(len(self.gradientInfo)):
            gradientInfoFlat[i] = np.array([*self.gradientInfo[i]['color'], self.gradientInfo[i]['position']])
        self.gradientInfoBuffer = cl.Buffer(self.ctx, flasg = self.mf.READ_ONLY, size = gradientInfoFlat.nbytes)
        cl.enqueue_copy(self.queue, self.gradientInfoBuffer, self.gradientInfo)
        
        
        #Create the buffers for the sies of arrays
        sizes = np.array(self.mask.size[0], self.mask.size[1], self.triangles.shape[0], dtype=np.uint16)
        self.sizeBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = sizes.nbytes)
        cl.enqueue_copy(self.queue, self.sizeBuffer, sizes)
    
        
        

    
    def Compute(self):
        programSource = ''
        with open('interpolation.c', 'r') as f:
            programSource = f.read()
            
        prg = cl.Program(self.ctx, programSource).build()
        
        prg.DelaunyInterpolation(self.queue, (self.mask.size[0], self.mask.size[1]), None,\
            self.triBuffer, self.imageBuffer,\
            self.sizeBuffer, self.gradientInfoBuffer, self.maxMinBuffer)
        
        self.output = np.zeros((self.resolution[1], self.resolution[0], 4), dtype=np.uint8)
        cl.enqueue_copy(self.queue, self.output, self.imageBuffer)
        
        return self.output


class interpolate_delauny_cpu():

    def __init__(self, points:np.ndarray, mask:PIL.Image.Image, maxMin:tuple, colorMode = 1, monocolorValues = None, clip = True):
        #Seperate the values of the points from said points
        self.pointValues = points[:, 2]
        self.points = points[:, :2]

        self.colorMode = colorMode
        
        #Determine the maximum and minimum value of the points
        self.minVal = maxMin[0]
        self.maxVal = maxMin[1]
            

        #Determines what shade of color will a value be
        self.valueImpact = (self.maxVal-self.minVal)/255

        #Create other class values
        self.monocolorValues = monocolorValues
        self.mask = mask
        self.clip = clip
        self.resolution = mask.size

        self.mask = np.array(self.mask)

        self.triangles = self.CreateTriangles()



    def VisualizeTriangles(self, xlim = (-100, 2000), ylim = (-100, 1500)):


        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        fig, ax = plt.subplots()

        ax.set_xlim(xlim[0], xlim[1])
        ax.set_ylim(ylim[0], ylim[1])
        for triangle in self.triangles:
            ax.add_patch(patches.Polygon(triangle[:, :2], True, edgecolor='red', facecolor='none'))

        plt.show()


    
    def CreateTriangles(self):

        #Create the triangles from the points
        triangles = Delaunay(self.points)

        #Create the outputs for triangles
        triangleOutput = np.empty((triangles.simplices.shape[0], 3, 3), dtype=np.int32)

        #Extract the triangles from the simplices (not sure what that is honestly)
        for i, simplex in enumerate(triangles.simplices):
            triangle = [np.array([self.points[index][0], self.points[index][1], self.pointValues[index]]) for index in simplex]
            triangleOutput[i] = triangle

        return triangleOutput
        
    

    def Interpolate(self):

        #Create the outputs for the output image
        imageOutput = np.zeros(shape=(self.resolution[1], self.resolution[0], 4), dtype = np.uint8)
        
        grad = gradient((self.minVal, self.maxVal), ReadSettings.Settings()["gradient"])

        def middle(a, b, c):
                if b>=a and b<=c:
                    return b
                elif b<a:
                    return a
                else: return c
        #Run the interpolation loop trough the triangle
        def InterpolateTriangle(xRange, kPart, kFull, rPart, rFull):
            
            #Loop trough the middle and 1st or 2nd point
            for x in range(xRange[0], xRange[1]):

                #Calculate the Y coordinates for the givven X coordinates
                yRange = [middle(0, math.ceil(kPart*x+rPart), self.resolution[1]), middle(0, math.ceil(kFull*x+rFull), self.resolution[1])]
                


                #Create a list of y coordinates  
                yList = np.arange(start=min(yRange), stop = max(yRange))
                for y in yList:
                    if self.mask[y][x][0] == 0:
                        continue
                    
                    #Break the triangle into 3 by creating edge from curent point to vertecies of triangle
                    a = abs(triangle[0][0]*(triangle[1][1]-y) + triangle[1][0]*(y-triangle[0][1]) + x*(triangle[0][1]-triangle[1][1]))
                    b = abs(triangle[0][0]*(y-triangle[2][1]) + x*(triangle[2][1]-triangle[0][1]) + triangle[2][0]*(triangle[0][1]-y))
                    c = abs(x*(triangle[1][1]-triangle[2][1]) + triangle[1][0]*(triangle[2][1]-y) + triangle[2][0]*(y-triangle[1][1]))
                    
                    #Calculate the value of the pixel
                    val = (triangle[2][2]*a+triangle[1][2]*b+triangle[0][2]*c)/(a+b+c)

                    #Colors
                    imageOutput[y][x] = [*grad.GetColorAtPoint(val), 255]



        #Loop trought the triangles and calculate the values of each pixel in them
        for triangle in self.triangles:

            #Sort the triangle by its X coordinate in ascending order
            triangle = triangle[triangle[:, 0].argsort()][::1]

            #f(x) = k*x + r
            #Find the kooficients of the functions for each edge of the triangle
            k01 = 0
            k12 = 0
            k02 = 0

            if triangle[1][0]-triangle[0][0]!= 0: 
                k01 = (triangle[1][1]-triangle[0][1])/(triangle[1][0]-triangle[0][0])
            else: k01 = None
            
            if triangle[1][0]-triangle[2][0]!= 0: 
                k12 = ((triangle[1][1]-triangle[2][1])/(triangle[1][0]-triangle[2][0])) 
            else: k12 = None
            
            k02 = ((triangle[0][1]-triangle[2][1])/(triangle[0][0]-triangle[2][0])) 
            
            #Find the r in the function for each edge)
            r01 = 0
            r12 = 0
            r02 = 0

            if k01 != None:
                r01 = triangle[1][1]-triangle[1][0]*k01
            if k12 != None:
                r12 = triangle[1][1]-triangle[1][0]*k12
            r02 = triangle[0][1]-triangle[0][0]*k02

            # X coordinates trough which to interpolate, replaces the out of bounds coordinates with 0 or resolution x
            xRange = [middle(0, triangle[0][0], self.resolution[0]), \
                    middle(0, triangle[1][0], self.resolution[0]), \
                    middle(0, triangle[2][0], self.resolution[0])]
           
            #Call the Interpolate triangle function for boths sides of  the triangle
            InterpolateTriangle((xRange[0], xRange[1]), k01, k02, r01, r02)
            InterpolateTriangle((xRange[1], xRange[2]), k12, k02, r12, r02)
        
        
        return (imageOutput, self.maxVal, self.minVal)


        
class InterpolationIDW_GPU():
    def __init__(self, points, image:PIL.Image.Image, tree:np.ndarray,  maxPPP = None, interactive = False) -> None:
        self.ctx = cl.create_some_context(interactive=interactive)
        self.queue = cl.CommandQueue(self.ctx)
        self.mf = cl.mem_flags

        self.points = points
        self.resolution = image.size
        self.image = np.array(image)
        self.tree = tree
        #Check if max points per pixel is more than there are points
        if maxPPP == None:
            maxPPP = len(self.points)
        elif maxPPP > len(self.points):
            maxPPP = len(self.points)
        self.maxPPP = maxPPP

        self.createBuffers()

    def createBuffers(self) -> list: #width, height
        #resolution = [2, 4]

        self.resolution = 0
            
        #Dimentions of the distance data - known points; y; x;
        #Create array to store distances form pixels to known points

        #self.dist = np.full((self.maxPPP, self.resolution[0], self.resolution[1], 2),-1, dtype=np.float32)
        #print(self.dist.nbytes)
        
        self.points = self.points.astype(np.uint16)
        
        
        #Create the buffers
        self.treeBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_WRITE, size = self.dist.nbytes)
        self.pointsBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = self.points.nbytes)
        #self.distShapeBuffer = cl.Buffer(self.ctx, flags = self.mf.READ_ONLY, size = np.array((self.maxPPP, self.resolution[0], self.resolution[1], len(Points)), dtype=np.uint16).nbytes)
        
        print(self.dist.nbytes*10**-9)
        #Copy the data to buffers in memory
        cl.enqueue_copy(self.queue, self.pointsBuffer, self.points)
        cl.enqueue_copy(self.queue, self.distShapeBuffer, np.array(self.dist.shape, dtype=np.uint16))
    

    
    def compute(self):
        programSource = ''
        with open('interpolation2.c', 'r') as f:
            programSource = f.read()
            
        prg = cl.Program(self.ctx, programSource).build()
        
        prg.CalculateDistances(self.queue, (self.resolution[0], self.resolution[1]), None, self.distShapeBuffer, self.pointsBuffer, self.distBuffer)

        cl.enqueue_copy(self.queue, self.dist, self.distBuffer)
        print(self.dist)



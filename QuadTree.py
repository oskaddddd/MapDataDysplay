import numpy as np


class Node:
    def __init__(self, xRange = [0, 0], yRange = [0, 0], quad=-1, parent=-1, children=[-1, -1, -1, -1], pointIndex = -1):
        self.quad = quad
        self.parent = parent
        self.children = children
        self.pointIndex = pointIndex
        self.xRange = xRange
        self.yRange = yRange
        self.mid = [abs(xRange[1]-xRange[0])//2, abs(yRange[1]-yRange[0])//2]

    def GetMid(self):
        self.mid = [(self.xRange[0]+(self.xRange[1]-self.xRange[0])//2), (self.yRange[0]+(self.yRange[1]-self.yRange[0])//2)]
    def All(self):
        return [self.xRange,self.yRange, self.mid, self.quad, self.parent, self.children, self.pointIndex]
    def Debug(self):
        out = ''
        out += f"xRang:{self.xRange}, yRang:{self.yRange}, Quad:{self.quad}, IsLeaf:{('False, indexes:' +str(self.children))if self.children[0]!= -1 else True}, HasPoint:{False if self.pointIndex == -1 else ('True, Index =' +str(self.pointIndex))}, Parent:{self.parent}"
        return out

class QuadTree:
    def __init__(self, xRange, yRange, points):
        self.points = points
        self.debug = 0
        #An array that contains all the nodes in class form,
        #will be flatened later in the flattened function using Node.all() function
        self.tree = [Node(xRange=xRange, yRange=yRange)]

        #Add a 0 to the end of every embeded array (1, 1, 1) -> (1, 1, 1, 0)
        self.outPoints = np.append(points, np.zeros((points.shape[0], 1)), 1)

        #Insert each point into the quad tree
        for i, p in enumerate(points):
            print('main - moving to next point...')
            self.InsertPoint(0, i)

    def InsertPoint(self, nodeIndex, pointIndex):

        self.debug +=1
        if self.debug == 20:
            exit()
        print('\n***INSERT POINT***\n')
        print('point node index:', pointIndex, nodeIndex, self.points[pointIndex])
        point = self.points[pointIndex]
        print('Node:',self.tree[nodeIndex].All())
        #If node is a leaf node
        if self.tree[nodeIndex].children[0] == -1:
            print ('Jeh.. last leave')  
            print('1if:', 1, 'is leaf')
            #If the leaf node has any points alreadyy stored in them
            if self.tree[nodeIndex].pointIndex != -1:
                print('2if:', 3, 'has points')
                self.Subdivide(nodeIndex)
                
                #Determine in which quad the point lies and the index of said node
                childQuadIndex = self.GetQuad(self.tree[nodeIndex].mid, point)
                childNodeIndex = self.tree[nodeIndex].children[childQuadIndex]
                print('Created Children:',self.tree[childNodeIndex].Debug())
                print('Updated Node:',self.tree[nodeIndex].Debug(), '\n')
                #Recursive InsertPoint top the new node (climb up the tree)
                self.InsertPoint(childNodeIndex, pointIndex)
                

            #If leaf node is empty
            else:
                print('2if:', 4, 'leaf node is empty')
                #Save the index of the points to the node and index of the node to the point
                self.tree[nodeIndex].pointIndex = pointIndex
                self.outPoints[pointIndex] = np.append(point, nodeIndex)
                   
        #If node isn't a leaf node
        else:
            
            #Determine in which quad the point lies and the index of said node
            childQuadIndex = self.GetQuad(self.tree[nodeIndex].mid, point)
            childNodeIndex = self.tree[nodeIndex].children[childQuadIndex]
            print('1if:', 2, 'isnt leaf node', childNodeIndex)
            #Recursive InsertPoint top the new node (climb up the tree)
            self.InsertPoint(self.tree[nodeIndex].children[childQuadIndex], pointIndex)
        
        
        


    def Subdivide(self, nodeIndex):

        print('\n***SUBDIVIDE***\n')
        #Create a list of nodes with the parent node of the input node and the correct quad
        childNodes = [Node(parent=nodeIndex, quad=i) for i in range(4)]

        #Set the dimmentsions of the nodes
        childNodes[0].xRange = [self.tree[nodeIndex].mid[0], self.tree[nodeIndex].xRange[1]]
        childNodes[0].yRange = [self.tree[nodeIndex].mid[1], self.tree[nodeIndex].yRange[1]]

        childNodes[1].xRange = [self.tree[nodeIndex].mid[0], self.tree[nodeIndex].xRange[1]]
        childNodes[1].yRange = [self.tree[nodeIndex].yRange[0], self.tree[nodeIndex].mid[1]]

        childNodes[2].xRange = [self.tree[nodeIndex].xRange[0], self.tree[nodeIndex].mid[0]]
        childNodes[2].yRange = [self.tree[nodeIndex].yRange[0], self.tree[nodeIndex].mid[1]]

        childNodes[3].xRange = [self.tree[nodeIndex].xRange[0], self.tree[nodeIndex].mid[0]]
        childNodes[3].yRange = [self.tree[nodeIndex].mid[1], self.tree[nodeIndex].yRange[1]]
        
        for node in childNodes:
            node.GetMid()
        #Add the children node indeces to the parent node
        #self.tree[nodeIndex].children = [len(self.tree) + x for x in range(4)]
            

        #Get the quad in which the parents point now lies
        childQuadIndex = self.GetQuad(self.tree[nodeIndex].mid, self.points[self.tree[nodeIndex].pointIndex])
        #Transfer the parents point to child and remove parents point
        childNodes[childQuadIndex].pointIndex = self.tree[nodeIndex].pointIndex    
        
        for x in range(4):
            childNodes[x].children = [-1, -1, -1, -1]
            self.tree.append(childNodes[x])
            self.tree[nodeIndex].children[x]  = len(self.tree)-1    
        
        self.tree[nodeIndex].pointIndex = -1
        print ('Working node data after split')
        print(self.tree[nodeIndex].All())
        


        #self.tree[nodeIndex].children[0]  = len(self.tree) 
        #self.tree[nodeIndex].children[1]  = len(self.tree) + 1
        #self.tree[nodeIndex].children[2]  = len(self.tree) + 2
        #self.tree[nodeIndex].children[3]  = len(self.tree) + 3
        #[len()]
        #print("Child indexes:", self.tree[nodeIndex].children)

        
        #childQuadIndex = self.GetQuad(self.tree[nodeIndex].mid, self.points[self.tree[nodeIndex].pointIndex])
        

        #print('Node Child3:',childNodes[childQuadIndex].All(), nodeIndex)
        #Add the children nodes to main node list
        #self.tree += childNodes
        




    def GetQuad(self, center, point):
        ##print(center, point)
        #Get the quadraint that a point belongs to acording to the center
        if center[0] <= point[0] and center[1] < point[1]:
            return 0
        elif center[0] > point[0] and center[1] <= point[1]:
            return 1
        elif center[0] >= point[0] and center[1] > point[1]:
            return 2
        elif center[0] < point[0] and center[1] >= point[1]:
            return 3
        


    def Flatten(self):
        pass

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def add_rectangle(ax, x_range, y_range, edgecolor='red', facecolor='none'):
    """
    Add a rectangle to the given axis.

    Parameters:
    - ax: Matplotlib axis object
    - x_range: List or tuple representing the x-axis range [xMin, xMax]
    - y_range: List or tuple representing the y-axis range [yMin, yMax]
    - edgecolor: Outline color of the rectangle (default: 'red')
    - facecolor: Fill color of the rectangle (default: 'none')
    """
    # Create a rectangle patch
    rectangle = patches.Rectangle((x_range[0], y_range[0]), x_range[1] - x_range[0], y_range[1] - y_range[0],
                                  edgecolor=edgecolor, facecolor=facecolor)

    # Add the rectangle patch to the axis
    ax.add_patch(rectangle)


def Test():
    
    points = np.random.randint(0, 100, size=(4, 3))

    print(points)
    fig, a1 = plt.subplots()

    # Set axis limits
    a1.set_xlim(0, 100)
    a1.set_ylim(0, 100)
    for x in points:
        a1.scatter(x[0], x[1], marker='o', color='red')
        print(x)
    plt.show()
    quad = QuadTree((0, 100), (0, 100), points)


    # Create a figure and axis
    fig, ax = plt.subplots()

    # Set axis limits
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)

    # Use the function to add a rectangle with specified x and y ranges
    colors = ['red', 'blue', 'yellow', 'green', 'black', 'cyan', 'magenta']
    for i, x in enumerate(quad.tree):
        print(x.Debug())
        if x.children[0] == -1:
            add_rectangle(ax, x.xRange,x.yRange,"black",colors[i%7])
    for x in quad.outPoints:
        ax.scatter(x[0], x[1], marker='o', color='white')
        print(x)

    # Display the plot
    plt.show()
Test()

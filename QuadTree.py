import numpy as np

class Node:
    def __init__(self, dimension, placement=-1, parent=-1, children=np.array([-1, -1, -1, -1]), containedPoins = 0):
        self.placement = placement
        self.parent = parent
        self.children = children
        self.pointIndex = -1
        self.dimmension = dimension
        self.mid = [dimension[0]//2, dimension[1]//2]

        
    def all(self):
        return np.array(self.dimmension, self.placement, self.parent, self.children)

class QuadTree:
    def __init__(self, corners, points):
        self.points = points

        #An array that contains all the nodes in class form,
        #will be flatened later in the flattened function using Node.all() function
        self.tree = [Node(dimension=corners)]

        #Add a 0 to the end of every embeded array (1, 1, 1) -> (1, 1, 1, 0)
        self.outPoints = np.append(points, np.zeros((points.shape[0], 1)), 1)

        #Insert each point into the quad tree
        for i, p in enumerate(points):
            self.InsertPoint(p, 0, i)

    def InsertPoint(self, point, nodeIndex, pointIndex):

        if self.tree[nodeIndex].children[0] != -1:
            if self.tree[nodeIndex].pointIndex != -1:
                self.Subdivide()
                pass
            else:
                #Save the index of the points to the node and index of the node to the point
                self.tree[nodeIndex].pointIndex = nodeIndex
                self.outPoints[pointIndex] = np.append(point, nodeIndex)
                return   
        else:
            pass




    def CreateQuadTree(self, node: Node):
        np.append(self.out, node.all())


    def Flatten(self):
        pass
        


    def Subdivide(dimmension):
        pass

    def GetQuadrant(node: Node, point):


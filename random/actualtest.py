import numpy as np


points = np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3]])

points = np.append(points, np.zeros((points.shape[0], 1)), 1)
print(points)
t = np.array([1, 2, 3])
points[1, :3] = t
print(points) 
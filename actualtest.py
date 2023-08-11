import numpy as np

def create_dots(resolution):
    x_coords = np.arange(resolution[0])
    y_coords = np.arange(resolution[1])
    xx, yy = np.meshgrid(x_coords, y_coords)
    dots = np.dstack((xx, yy, np.zeros_like(xx)))
    return dots

print(create_dots([10, 5]))
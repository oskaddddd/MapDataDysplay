import numpy as np
import matplotlib.pyplot as plt

# Define the points
point1 = np.array([0, 0])
point2 = np.array([1, 1])

# Calculate the third point on the line y = -x + 1
v = 0.5 # Adjust v within the range [-0.4, 0.4] as needed
point3_x = 0.5 + v
point3_y = -point3_x + 1
point3 = np.array([point3_x, point3_y])

# Calculate control points for cubic Bézier curve
control_point1 = point3


# Generate points along the curve (cubic Bézier curve)
t = np.linspace(0, 1, 100)
curve_x = 3 * (1 - t) ** 2 * t * control_point1[0] + 3 * (1 - t) * t ** 2 * control_point1[0] + t ** 3 * point2[0]
curve_y = (1 - t) ** 3 * point1[1] + 3 * (1 - t) ** 2 * t * control_point1[1] + 3 * (1 - t) * t ** 2 * control_point1[1] + t ** 3 * point2[1]

# Plot the curve
plt.plot(curve_x, curve_y, label='Smooth L-shaped Curve')
plt.scatter([point1[0], point3[0], point2[0]], [point1[1], point3[1], point2[1]], color='red', label='Given Points')
plt.scatter([control_point1[0], control_point1[0]], [control_point1[1], control_point1[1]], color='blue', label='Control Points')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Smooth L-shaped Curve with weighted 2nd point')
plt.legend()
plt.grid(True)
plt.show()
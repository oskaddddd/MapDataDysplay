from scipy.interpolate import CubicSpline

def bezier_curve(control_points, t):
    """
    Calculate the point on the cubic Bézier curve for a given parameter t.
    
    Parameters:
        control_points (list of tuples): The control points of the cubic Bézier curve.
        t (float): Parameter ranging from 0 to 1.
    
    Returns:
        tuple: The (x, y) coordinates of the point on the curve at parameter t.
    """
    # Unpack control points
    P0, P1, P2, P3 = control_points
    
    # Calculate x and y coordinates using the cubic Bézier curve formula
    x = (1 - t)**3 * P0[0] + 3 * (1 - t)**2 * t * P1[0] + 3 * (1 - t) * t**2 * P2[0] + t**3 * P3[0]
    y = (1 - t)**3 * P0[1] + 3 * (1 - t)**2 * t * P1[1] + 3 * (1 - t) * t**2 * P2[1] + t**3 * P3[1]
    
    return x, y

def index_curve_at_x(control_points, x_values):
    """
    Index the curve at certain x values and return corresponding y values.
    
    Parameters:
        control_points (list of tuples): The control points of the cubic Bézier curve.
        x_values (list of floats): The x values where to index the curve.
    
    Returns:
        list of floats: The corresponding y values on the curve for the given x values.
    """
    # Calculate the y values for each x value
    y_values = []
    for x in x_values:
        # Use scipy.interpolate.CubicSpline to find the y value
        t_guess = 0.5  # Initial guess for parameter t (can be adjusted)
        x_curve = lambda t: bezier_curve(control_points, t)[0]
        t_solution = newton(x_curve, t_guess)
        y_values.append(bezier_curve(control_points, t_solution)[1])
    return y_values

# Example usage
control_points = [(0, 0), (0.8, 0.2), (1, 0)]  # Example control points
x_values = [0.25, 0.5, 0.75]  # Example x values to index the curve

y_values = index_curve_at_x(control_points, x_values)
print("Corresponding y values:", y_values)

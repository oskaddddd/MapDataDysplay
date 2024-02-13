import numpy as np
a = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
a[0:9] = a[3:12]
print(a)
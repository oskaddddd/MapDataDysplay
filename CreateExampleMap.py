import random
import json
from perlin_noise import PerlinNoise

grid = False

n = 1000
corners = [[53.85405444949857, 20.840097270351063], [56.60326420819254, 27.22864675471188]]
cy = sorted([corners[0][1], corners[1][1]])
cx = sorted([corners[0][0], corners[1][0]])

arr = []

if grid:

    y1 = abs(cy[0] - cy[1])
    x1 = abs(cx[0] - cx[1])

    k2 = n/(x1*y1)
    k1 = k2**0.5

    x2 = round(x1*k1)
    y2 = round(y1*k1)

    

    noise = PerlinNoise(octaves=7, seed=986792)

    nx = 1
    ny = 1
    val = 10
    for xi in range(x2):
        for yi in range(y2):
            c1 = random.randrange(95, 105)/100*(xi/k1+min(cx))
            c2 = random.randrange(95, 105)/100*(yi/k1+min(cy))
            arr.append({"GPS": [str(c1), str(c2)], "Value": int((noise([c1*val, c2*val])))})
            #print([mx+kkx*xi, my+kky*yi])
else:
    ran = [13, 60]
    cy = [int(cy[0]*10**10), int(cy[1]*10**10)]
    cx = [int(cx[0]*10**10), int(cx[1]*10**10)]
    noise = PerlinNoise(octaves=3, seed=734582)
    x = 1
    for _ in range(n):
        
        #print(_)
        dat = [random.randrange(cx[0], cx[1])/10**10, random.randrange(cy[0], cy[1])/10**10]
        arr.append({"GPS": [str(dat[0]), str(dat[1])], "Value": int((noise([dat[0]*x, dat[1]*x])+1)*50)})

with open('data.json', 'w') as f:
    json.dump(arr, f, indent=2)



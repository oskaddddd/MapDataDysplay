from perlin_noise import PerlinNoise

noise = PerlinNoise(octaves=10, seed=1)
for x in range(100):
     for y in range(100):
          print((noise([x/100, y/100])+1)*50)
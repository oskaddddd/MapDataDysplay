from tkinter import *
import PIL.Image
import numpy as np
import json
import time
from gpushittest import createPixel

#Get image name
imageName = ''
with open('ImageName.txt', 'r') as f:
    imageName = f.read()
    
    imageName = imageName[:imageName.index('.')+1]+'png' \
    if imageName[imageName.index('.')+1:] != 'png' \
    else imageName
    print(imageName)

#calibration
cali = []

#Get calibration data
try:
    with open('CoordinateCalibration.json',) as f:
        cali = json.load(f)
        if cali == [[[0, 0], 0], [[0, 0], 0]]:
            exit()
except:
    print('Please set 2 calibration coordinates in Calibration.py')
    exit()
    
#Calculate the decoding values
cali[0]['GPS'].reverse()
cali[1]['GPS'].reverse()

k = [(cali[0]['Pixel'][0]-cali[1]['Pixel'][0])/(float(cali[0]['GPS'][0])-float(cali[1]['GPS'][0])),
     (cali[0]['Pixel'][1]-cali[1]['Pixel'][1])/(float(cali[0]['GPS'][1])-float(cali[1]['GPS'][1]))]
b = [cali[0]['Pixel'][0]-(k[0]*float(cali[0]['GPS'][0])),
     cali[0]['Pixel'][1]-(k[1]*float(cali[0]['GPS'][1]))]
print(cali, k, b)

#Decoding function
def Decode(cords:list):
    return [round(float(cords[1])*k[0]+b[0]), round(float(cords[0])*k[1]+b[1])]
t2 = time.time()
data = []
mapData = []
image = PIL.Image.open(imageName)
print(time.time()-t2)
t2 = time.time()
with open('data.json', 'r') as f:
    data = json.load(f)
print(time.time()-t2)
t2 = time.time()
for x in data:
    #if t["Pixel"][0] < image.size[0] and t["Pixel"][1] < image.size[1] and t["Pixel"][0] > 0 and t["Pixel"][1] > 0:
    n = Decode(x["GPS"])
    mapData.append([n[0], n[1], x["Value"]])
print(time.time()-t2)


#Interpolation Function on the gpu
def SmoothGpu(points):
    t1 = time.time()
    #points = [[x["Pixel"][0], x["Pixel"][1], x["Value"]] for x in points]
    
    creator = createPixel(False)
    print(time.time()-t1)
    t1 = time.time()
    creator.createPixelBuffer(image.size, Image=image)
    print(time.time()-t1)
    t1 = time.time()
    creator.createTriangles(points=np.array(points), Mode=0, showTriangles=False)
    print(time.time()-t1)
    t = time.time()
    res = creator.compute()
    print(time.time()-t, time.time()-t1)
    
    return res.astype(np.uint8)

#Debugging function to see where the points are placed
def ShowPoints(Points):
    imageArr = np.array(image)
    for x in Points:
        imageArr[x["Pixel"][1]][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]+1][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]-1][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]][x["Pixel"][0]+1] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]][x["Pixel"][0]-1] = [255, 0, 0, 255]
    PIL.Image.fromarray(imageArr).show()

arr = SmoothGpu(mapData)
PIL.Image.fromarray(arr).show()


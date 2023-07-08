from tkinter import *
import PIL.Image
import numpy as np
import json

imageName = ''
with open('ImageName.txt', 'r') as f:
    imageName = f.read()
    
    imageName = imageName[:imageName.index('.')+1]+'png' \
    if imageName[imageName.index('.')+1:] != 'png' \
    else imageName
    print(imageName)


cali = []
try:
    with open('CoordinateCalibration.json',) as f:
        cali = json.load(f)
        if cali == [[[0, 0], 0], [[0, 0], 0]]:
            #print('Please set 2 calibration coordinates in Calibration.py')
            exit()
        print(cali)
except:
    print('Please set 2 calibration coordinates in Calibration.py')
    exit()
cali[0]['GPS'].reverse()
cali[1]['GPS'].reverse()
print(cali)
k = [(cali[0]['Pixel'][0]-cali[1]['Pixel'][0])/(float(cali[0]['GPS'][0])-float(cali[1]['GPS'][0])),
     (cali[0]['Pixel'][1]-cali[1]['Pixel'][1])/(float(cali[0]['GPS'][1])-float(cali[1]['GPS'][1]))]
print(k)
b = [cali[0]['Pixel'][0]-(k[0]*float(cali[0]['GPS'][0])),
     cali[0]['Pixel'][1]-(k[1]*float(cali[0]['GPS'][1]))]
print(b)

def Decode(cords:list):
    return [round(float(cords[1])*k[0]+b[0]), round(float(cords[0])*k[1]+b[1])]

data = []
mapData = []

image = PIL.Image.open(imageName)
def Dysplay():
    imageArr = np.array(image)
    for x in mapData:
        imageArr[x["Pixel"][1]][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]+1][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]-1][x["Pixel"][0]] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]][x["Pixel"][0]+1] = [255, 0, 0, 255]
        imageArr[x["Pixel"][1]][x["Pixel"][0]-1] = [255, 0, 0, 255]
    PIL.Image.fromarray(imageArr).show()
with open('data.json', 'r') as f:
    data = json.load(f)
    print(data) 
for x in data:
    t = {}
    t["Pixel"] = Decode(x["GPS"])
    t["Value"] = x["Value"]
    if t["Pixel"][0] < image.size[0] and t["Pixel"][1] < image.size[1] and t["Pixel"][0] > 0 and t["Pixel"][1] > 0:
        mapData.append(t)
    print(t)
print(mapData)

Dysplay()

inp = [43.784839409483716, 7.534168032407811]
print(inp)
inp.reverse()
print(Decode(cords=inp))
root = Tk()

hello = Label(root, text="Hello world")  
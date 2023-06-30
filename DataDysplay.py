from tkinter import *
import PIL
import numpy as np
import json

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
k = [(cali[0]['Pixel'][0]-cali[1]['Pixel'][0])/(float(cali[0]['GPS'][0])-float(cali[1]['GPS'][0])), (cali[0]['Pixel'][1]-cali[1]['Pixel'][1])/(float(cali[0]['GPS'][1])-float(cali[1]['GPS'][1]))]
print(k)
b = [float(cali[0]['Pixel'][0])-(k[0]*float(cali[0]['GPS'][0])), float(cali[0]['Pixel'][1])-(k[1]*float(cali[0]['GPS'][1]))]
print(b)

def Decode(cords:list):
    
    return [round(float(cords[0])*k[0]+b[0]), round(float(cords[1])*k[1]+b[1])]

data = []

inp = [43.784839409483716, 7.534168032407811]
print(inp)
inp.reverse()
print(Decode(cords=inp))
root = Tk()

hello = Label(root, text="Hello world")  
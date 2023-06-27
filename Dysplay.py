import PIL.Image
import PIL.ImageTk
import numpy as np
from tkinter import *
import json

image = PIL.Image.open('mask.png').convert('RGBA')

#raise the threshold not the entire region is green and lower it if pixels outside the region are green
threashhold = 100

defImageArr = np.array(image)
imageArr = defImageArr.copy()
print("Loaded image into array")

print("Coloring region green... this might take abit")
for i1, y in enumerate(defImageArr):
    for i2, x in enumerate(y):
        if x[0] < threashhold:
            defImageArr[i1][i2] = np.array([0, 255, 0, 255])
        else:
            defImageArr[i1][i2] = np.array([0, 0, 0, 0])
imageArr = defImageArr.copy()
image = PIL.Image.fromarray(imageArr)

print("Colored region green")
print("Prepearing GUI... This might take abit")

root = Tk()
root.minsize(image.size[0], image.size[1])
root.title("Image to real world calibration")

imTK = PIL.ImageTk.PhotoImage(image)

Im = Label(root, image=imTK)
Info = Label(root, text=f"Enter rl coordinates for selected pixel {0, 0}, seperated by a space")

entry = Entry(root, width=40)
selected = [0, 0]
editing = 1 #vars 1 or 2

datList = []
with open('CoordinateCalibration.json', 'r') as f:
    datList=json.load(f)
print("Read json data")
dat = Label(root, text=f"\n[Picture cords] -- [Real life cords]\nPoint 1:{datList[0][0]} -- {datList[0][1]}\nPoint 2:{datList[1][0]} -- {datList[1][1]}")

def click(e):
    global imTK
    global Im
    global imageArr
    global selected
    
    if e.y < image.size[1] and e.x < image.size[0]:
        if (defImageArr[e.y-1][e.x-1] == np.array([0, 255, 0, 255])).all():
            imageArr = defImageArr.copy()
            selected = [e.x-1, e.y-1]
            print(f"Registered a click at {selected}")
    
        
            red = np.array([255, 0, 0, 255])
            imageArr[selected[1]][selected[0]] = red
            imageArr[selected[1]+1][selected[0]] = red
            imageArr[selected[1]-1][selected[0]] = red
            imageArr[selected[1]][selected[0]+1] = red
            imageArr[selected[1]][selected[0]-1] = red
            print("Set pressed pixels to red")
            
            imTK = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(imageArr))
            Im = Label(root, image=imTK)
            Info = Label(root, text=f"Enter rl coordinates for selected pixel {selected[0], selected[1]}, seperated by a space, latitude then longitude")
            Info.grid(row=2, column=0)   
            Im.grid(row=1, column=0)
            print('Updated Image and Coordinate dysplay')

def CordSubmit():
    global dat
    global datList
    t = entry.get()
   
    datList[editing-1][1] = t.split()
    datList[editing-1][0] = selected
    print(f"Read data {t.split()}")
    
    dat = Label(root, text=f"\n[Picture cords] -- [Real life cords]\nPoint 1:{datList[0][0]} -- {datList[0][1]}\nPoint 2:{datList[1][0]} -- {datList[1][1]}")
    dat.grid(row=1, column=1)
    print("Dysplayed new data")
    
    with open('CoordinateCalibration.json', 'w') as f:
        json.dump(datList, f)
    print("Wrote data to file")
    
    entry.delete("0","end")
    print("Cleared entry field")
        
butt = Button(root, text="Submit coordinates for point 1", command=CordSubmit)
    
def edit():
    global editing
    global butt
    
    editing = 1 if editing == 2 else 2
    print(f"Changed curent editing point to point {editing}")
    butt = Button(root, text=f"Submit coordinates for point {editing}", command=CordSubmit)
    butt.grid(row=4, column=0)
    print("Updated button text")
 
butt1 = Button(root, text=f"Change Point", command=edit)

Info.grid(row=2, column=0)
entry.grid(row=3, column=0)
butt.grid(row=4, column=0)
Im.grid(row=1, column=0)
butt1.grid(row=5, column=0)
dat.grid(row=1, column=1)
print("Loaded widgets")

root.bind('<1>',click)

print("Starting window...")
root.mainloop()

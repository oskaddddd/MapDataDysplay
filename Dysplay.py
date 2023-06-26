import PIL.Image
import PIL.ImageTk
import numpy as np
import time
from tkinter import *
import json
#from tkinter.ttk import *

image = PIL.Image.open('mask.png').convert('RGBA')
t = time.time()
threashhold = 100

defImageArr = np.array(image)
imageArr = defImageArr.copy()
print(imageArr[0])
print(time.time()-t)


for i1, y in enumerate(defImageArr):
    for i2, x in enumerate(y):
        if x[0] < threashhold:
            defImageArr[i1][i2] = np.array([0, 255, 0, 255])
        else:
            defImageArr[i1][i2] = np.array([0, 0, 0, 0])
imageArr = defImageArr.copy()
image = PIL.Image.fromarray(imageArr)


root = Tk()
root.minsize(image.size[0], image.size[1])
#root.maxsize(width=image.size[0]+1, height=100000)
#canva = Canvas(root, background="red")
imTK = PIL.ImageTk.PhotoImage(image)
root.title("ahhhhhh")
imTK = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(imageArr))
Im = Label(root, image=imTK)


Info = Label(root, text=f"Enter rl coordinates for selected pixel {0, 0}, seperated by a space")

text = Entry(root, width=40)
selected = [0, 0]
editing = 1 #vars 1 or 2

datList = []
with open('CoordinateCalibration.json', 'r') as f:
    
    datList=json.load(f)
dat = Label(root, text=f"\n[Picture cords] -- [Real life cords]\nPoint 1:{datList[0][0]} -- {datList[0][1]}\nPoint 2:{datList[1][0]} -- {datList[1][1]}")

def click(e):
    global imTK
    global Im
    global imageArr
    global selected
    
    print(datList)
    print(f"Pointer is currently at {e.x}, {e.y}")
    #text.pack()
    #print(text.get("1.0", "5.0"))
    if e.y < image.size[1] and e.x < image.size[0]:
        if (defImageArr[e.y-1][e.x-1] == np.array([0, 255, 0, 255])).all():
            Im.destroy()
            imageArr = defImageArr.copy()
            selected = [e.x-1, e.y]
    
        
            red = np.array([255, 0, 0, 255])
            imageArr[selected[1]][selected[0]] = red
            imageArr[selected[1]+1][selected[0]] = red
            imageArr[selected[1]-1][selected[0]] = red
            imageArr[selected[1]][selected[0]+1] = red
            imageArr[selected[1]][selected[0]-1] = red
            imTK = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(imageArr))
            Im = Label(root, image=imTK)
            Info = Label(root, text=f"Enter rl coordinates for selected pixel {selected[0], selected[1]}, seperated by a space, latitude then longitude")
            Info.grid(row=2, column=0)   
            Im.grid(row=1, column=0)
            
            
            
        #canva.place(x=e.x, y=e.y)
    

    
    
    
    #PIL.Image.fromarray(imageArr).show()
def CordSubmit():
    global dat
    global datList
    t = text.get()
    datList[editing-1][1][0] = 1
    datList[editing-1][1] = t.split()
    datList[editing-1][0] = selected
    print('GAyyyy', t.split(), datList)
    dat = Label(root, text=f"\n[Picture cords] -- [Real life cords]\nPoint 1:{datList[0][0]} -- {datList[0][1]}\nPoint 2:{datList[1][0]} -- {datList[1][1]}")
    dat.grid(row=6, column=0)
    text.delete("0","end")
    with open('CoordinateCalibration.json', 'w') as f:
        json.dump(datList, f)
    
butt = Button(root, text="Submit coordinates for point 1", command=CordSubmit)

    
def edit():
    global editing
    global butt
    
    editing = 1 if editing == 2 else 2
    
    butt = Button(root, text=f"Submit coordinates for point {editing}", command=CordSubmit)
    butt.grid(row=4, column=0)
    

        
    
    
butt1 = Button(root, text=f"Change Point", command=edit)


#canva.create_window(200, 140, window=text)
#canva.place(x=100, y=100)
Info.grid(row=2, column=0)
text.grid(row=3, column=0)
butt.grid(row=4, column=0)
Im.grid(row=1, column=0)
butt1.grid(row=5, column=0)
dat.grid(row=6, column=0)
root.bind('<1>',click)

#canva.pack()


root.mainloop()

# image.show()
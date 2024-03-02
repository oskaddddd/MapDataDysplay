#from tkinter import *
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
import time
import Interpolation
import ReadSettings
import QuadTree

settings = ReadSettings.Settings(True)

def prepare_data(data = None):
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
    print(data)
    if data == None:
        #Read the data.json
        print(data)
        data = []
        with open('data.json', 'r') as f:
            data = json.load(f)
        
    #Create the points array
    points = np.empty((len(data), 3))
    
    #Decode the data from data.json and add it to the points array
    for i, point in enumerate(data):
        n = [round(float(point["GPS"][1])*k[0]+b[0]), round(float(point["GPS"][0])*k[1]+b[1])]
        points[i] = np.array([n[0], n[1], point["Value"]])
    
    #Write the points to a json file
    with open('points.json', 'w')as f:
        print(points)
        json.dump(points.tolist(), f, indent=4)
    #
    ##Get all the x and y coordinates of the points
    #xPoints = points[:,0]
    #yPoints = points[:,1]
    #
    ##Calculate the bounding box of the points
    #xRange = [np.min(xPoints), np.max(xPoints)]
    #yRange = [np.min(yPoints), np.max(yPoints)]
    #
    #print(xRange, yRange)
    #
    ##Build the tree form the points
    #tree = QuadTree.QuadTree(points, xRange, yRange).Flatten(dtype = np.int16)
    #
    ##Write the tree to a json file
    #with open('tree.json', 'w') as f:
    #    print(tree)
    #    json.dump(tree.tolist(), f, indent=4)
    
    
class create_map():
    def __init__(self) -> None:
        self.image = PIL.Image.open(settings['image_name'])
        
        
    #Read the points and tree data from a json
    def ReadData(self):
        try:
            with open('points.json', 'r')as f:
                self.points = np.array(json.load(f))
            #with open('tree.json', 'r')as f:
            #    self.tree = np.array(json.load(f))
        except ValueError as e:
            return f'Failed to read data. Try loading it first. ({e})'
        except Exception as e:
            return f'Unknown error: {e}'

        


    def Interpolate(self):

        mode = settings["mode"]
        valueRange = None
        output = None
        
        
        
        #Gpu computation
        if settings["computation"].lower() == 'opencl':
            #IDW interpolation on the gpu
            if settings["interpolation"].lower() == 'idw':
                pass
                
            
            #Delauny triangulation on the gpu
            else:
                #Do the interpolation
                creator = Interpolation.interpolate_delauny_gpu(False)
                creator.createPixelBuffer(self.image.size, Image=self.image)
                valueRange = (creator.createTriangles(points=self.points, Mode=mode, showTriangles=False)[1:])
                output = creator.compute()
                
        #Delauny interpolation on the cpu 
        else:
            
            creator = Interpolation.interpolate_delauny_cpu(self.points, self.image, mode, None, settings['MonocolorId'], True)
            #creator.visualizeTriangles()
            o = creator.Interpolate()
            output = o[0]
            valueRange = (o[2], o[1])


        if settings["create_legend"] == True:
            steps = settings["sections"]
            textScale = settings["text_scale"]
            barSize = round(self.image.size[1]/(1.5*steps - 0.5)*settings["scale"])
            
            #Create the legend output array
            Legend = np.zeros((round(steps*barSize*1.5-barSize*0.5), 3*barSize, 4), dtype=np.uint8)

            units = ' '+settings["units"]

            #Create the texts array
            textLegend = np.zeros((round(steps*barSize*1.5-barSize*0.5), round(barSize*0.59*textScale*(settings["round_to"]+len(str(round(valueRange[1]))+units)))+10 + (8 if settings["round_to"] != 0 else 0), 4), dtype=np.uint8)
            
            #Turn the text array into an image and prapare it for drawing text onto it
            imText = PIL.Image.fromarray(textLegend)
            drawText = PIL.ImageDraw.Draw(imText)

            font = PIL.ImageFont.truetype("arial.ttf", round(barSize*textScale))
            
            #Add the colored bars to the legend (NEEDS REDOING)
            MonocolorId = settings['MonocolorId']
            for i in range(steps):

                barsColor = None
                if mode == 0:
                    val = round(255*(i/(steps-1)))

                    barsColor = np.array([val if MonocolorId[0] == 0 else MonocolorId[0], val if MonocolorId[1] == 0 else MonocolorId[1], val if MonocolorId[2] == 0 else MonocolorId[2], 255])
                elif mode == 1:
                    k = i/(steps-1)*4

                    if k >= 2.7:
                        barsColor = np.array([255, (4-k)*255/1.3, 0, 255])
                    elif k >= 2 and k < 2.7:
                        barsColor = np.array([(k-2)*255/4/0.7, 255, 0, 255])
                    elif k >= 1.3 and k < 2:
                        barsColor = np.array([0, 255, (2-k)*255/0.7, 255])
                    elif k < 1.3:
                        barsColor = np.array([0, k*255/1.3, 255, 255])
                    print(k)


                Legend[round(1.5*barSize*(steps-1-i)):round(1.5*barSize*(steps-1-i)+barSize), :barSize*3] = barsColor

                #Draw the text onto the the text image
                drawText.text((0,round(1.5*barSize*(steps-1-i)+((barSize-(barSize*textScale))/2))), " "+str(round((i/(steps-1))*(valueRange[1]-valueRange[0])+valueRange[0], settings["round_to"]))+units, font=font)

            textLegend = np.array(imText)
            
            #Join the text and legend arrays into one object
            LegendObj = np.concatenate((Legend, textLegend), axis=1, dtype=np.uint8)
            LegendObj = np.concatenate( ( np.zeros((round((self.image.size[1]-LegendObj.shape[0])*settings["vertical_position"]),  LegendObj.shape[1], 4), dtype = np.uint8),\
            LegendObj, np.zeros((self.image.size[1] - round((self.image.size[1]-LegendObj.shape[0])*settings["vertical_position"]+LegendObj.shape[0]),  LegendObj.shape[1], 4),  dtype = np.uint8)))

            #Join the image and legend
            if settings["horizontal_alignment"].lower() == 'left':
                output = np.concatenate((LegendObj, np.zeros((LegendObj.shape[0], settings["offset"], 4)), output), axis = 1)
            else:
                output = np.concatenate((output,np.zeros((LegendObj.shape[0], settings["offset"], 4)), LegendObj), axis = 1)
    
        return output.astype(np.uint8)

if __name__ == "__main__":
    magic = create_map()
    magic.Calibrate()
    #magic.DecodeData()
    magic.ReadData()
    t = time.time()
    image = magic.Interpolate()
    print('speed:', time.time()-t)
    
    PIL.Image.fromarray(image).show()


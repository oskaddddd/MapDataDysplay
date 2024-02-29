#from tkinter import *
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
import time
import Interpolation
import ReadSettings

settings = ReadSettings.Settings(True)

class create_map():
    def __init__(self) -> None:
        self.image = PIL.Image.open(settings['image_name'])
        
    #Calculates the values for all the points from data.json
    def Calibrate(self):
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

        self.k = [(cali[0]['Pixel'][0]-cali[1]['Pixel'][0])/(float(cali[0]['GPS'][0])-float(cali[1]['GPS'][0])),
                  (cali[0]['Pixel'][1]-cali[1]['Pixel'][1])/(float(cali[0]['GPS'][1])-float(cali[1]['GPS'][1]))]
        
        self.b = [cali[0]['Pixel'][0]-(self.k[0]*float(cali[0]['GPS'][0])),
                  cali[0]['Pixel'][1]-(self.k[1]*float(cali[0]['GPS'][1]))]


    def DecodeData(self):
        #Read the data.json
        data = []
        with open('data.json', 'r') as f:
            data = json.load(f)

        #Create the points array
        self.points = np.empty((len(data), 3))

        #Decode the data from data.json and add it to the points array
        for i, point in enumerate(data):
            n = [round(float(point["GPS"][1])*self.k[0]+self.b[0]), round(float(point["GPS"][0])*self.k[1]+self.b[1])]
            self.points[i] = np.array([n[0], n[1], point["Value"]])
        
        #Write the points to a json file
        with open('points.json', 'w')as f:
            print(self.points)
            json.dump(self.points.tolist(), f, indent=4)
    

    #Read the points and tree data from a json
    def ReadData(self):
        with open('points.json', 'r')as f:
            self.points = json.load(f)
        with open('tree.json', 'r')as f:
            self.tree = json.load(f)


    def Interpolate(self):

        mode = settings["mode"]
        valueRange = None
        output = None
        
        t = time.time()
        
        #Gpu computation
        if settings["computation"].lower() == 'opencl':
            #IDW interpolation on the gpu
            if settings["interpolation"].lower() == 'idw':
                import QuadTree
                
                #Get all the x and y coordinates of the points
                xPoints = self.points[:,0]
                yPoints = self.points[:,1]
                
                #Calculate the bounding box of the points
                xRange = [np.min(xPoints), np.max(xPoints)]
                yRange = [np.min(yPoints), np.max(yPoints)]
                
                print(xRange, yRange)
                
                #Build the tree form the points
                tree = QuadTree.QuadTree(self.points, xRange, yRange)
                QuadTree.VisualizeTree(tree)
                treeFlat = tree.Flatten(dtype = np.int16)
            
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
            Legend = np.zeros((round(steps*barSize*1.5-barSize*0.5), 3*barSize, 4), dtype=np.uint8)

            units = ' '+settings["units"]

            textLegend = np.zeros((round(steps*barSize*1.5-barSize*0.5), round(barSize*0.59*textScale*(settings["round_to"]+len(str(round(valueRange[1]))+units)))+10 + (8 if settings["round_to"] != 0 else 0), 4), dtype=np.uint8)

            print(barSize*textScale, 'wad')
            imText = PIL.Image.fromarray(textLegend)
            drawText = PIL.ImageDraw.Draw(imText)

            font = PIL.ImageFont.truetype("arial.ttf", round(barSize*textScale))
            #font = PIL.ImageFont.load_default()
            #deez nutz
            MonocolorId = settings['MonocolorId']
            for i in range(steps):

                barsColor = None
                if mode == 0:
                    val = round(255*(i/(steps-1)))

                    barsColor = np.array([val if MonocolorId[0] == 0 else MonocolorId[0], val if MonocolorId[1] == 0 else MonocolorId[1], val if MonocolorId[2] == 0 else MonocolorId[2], 255])
                    #print(barsColor, round(1.5*barSize*(steps-1-i)+barSize), round(1.5*barSize*(steps-1-i)), i/(steps-1), agenda.shape)
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

                drawText.text((0,round(1.5*barSize*(steps-1-i)+((barSize-(barSize*textScale))/2))), " "+str(round((i/(steps-1))*(valueRange[1]-valueRange[0])+valueRange[0], settings["round_to"]))+units, font=font)

            textLegend = np.array(imText)
            AgendaObj = np.concatenate((Legend, textLegend), axis=1, dtype=np.uint8)
            
            AgendaObj = np.concatenate( ( np.zeros((round((self.image.size[1]-AgendaObj.shape[0])*settings["vertical_position"]),  AgendaObj.shape[1], 4), dtype = np.uint8),\
            AgendaObj, np.zeros((self.image.size[1] - round((self.image.size[1]-AgendaObj.shape[0])*settings["vertical_position"]+AgendaObj.shape[0]),  AgendaObj.shape[1], 4),  dtype = np.uint8)))

            if settings["horizontal_alignment"].lower() == 'left':
                output = np.concatenate((AgendaObj, np.zeros((AgendaObj.shape[0], settings["offset"], 4)), output), axis = 1)
            else:
                output = np.concatenate((output,np.zeros((AgendaObj.shape[0], settings["offset"], 4)), AgendaObj), axis = 1)
        #print(res)
        return output.astype(np.uint8)

if __name__ == "__main__":
    magic = create_map()
    magic.Calibrate()
    magic.DecodeData()
    image = magic.Interpolate()
    
    PIL.Image.fromarray(image).show()


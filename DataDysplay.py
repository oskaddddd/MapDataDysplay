#from tkinter import *
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
import time
import Interpolation
import ReadSettings

class create_map():
    def __init__(self) -> None:
        self.settings = ReadSettings.Settings(True)
        self.imageName = self.settings["ImageName"]

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
        data = []

        image = PIL.Image.open(self.imageName)

        with open('data.json', 'r') as f:
            data = json.load(f)
        self.points = []

        for point in data:
            n = [round(float(point["GPS"][1])*self.k[0]+self.b[0]), round(float(point["GPS"][0])*self.k[1]+self.b[1])]
            self.points.append([n[0], n[1], point["Value"]])
        
        with open('points.json', 'w')as f:
            json.dump(self.points, f, indent=4)
        
    def ReadData(self):
        with open('points.json', 'r')as f:
            self.points = json.load(f)

    def Interpolate(self):

        points=np.array(points)
        Mode = self.settings["Mode"]
        lenth = None
        res = None

        t = time.time()
        if self.settings["Computation"].lower() == 'opencl':
            if self.settings["Interpolation"].lower() == 'idw':
                #creator = Interpolation.InterpolationIDW_GPU(False)


                import QuadTree
                xPoints = points[:,0]
                yPoints = points[:,1]

                xRange = [np.min(xPoints), np.max(xPoints)]
                yRange = [np.min(yPoints), np.max(yPoints)]
                print(xRange, yRange)
                tree = QuadTree.QuadTree(points, xRange, yRange)
                QuadTree.VisualizeTree(tree)
                treeFlat = tree.Flatten(dtype = np.int16)

            else:
                creator = Interpolation.interpolate_delauny_gpu(False)
                creator.createPixelBuffer(image.size, Image=image)
                lenth = (creator.createTriangles(points=points, Mode=Mode, showTriangles=False)[1:])
                res = creator.compute()
        else:
            creator = Interpolation.interpolate_delauny_cpu(points, image, Mode, None, self.settings['MonocolorId'], True)
            #creator.visualizeTriangles()
            o = creator.Interpolate()
            res = o[0]
            lenth = (o[2], o[1])

        print(time.time()-t)
    def CreateLegendy(self):
        if self.settings["CreateLegend"] == True:
            steps = self.settings["Sections"]
            textScale = self.settings["LegendTextScale"]


            barSize = round(image.size[1]/(1.5*steps - 0.5)*self.settings["LegendScale"])
            Legend = np.zeros((round(steps*barSize*1.5-barSize*0.5), 3*barSize, 4), dtype=np.uint8)

            units = ' '+self.settings["LegendUnits"]

            textLegend = np.zeros((round(steps*barSize*1.5-barSize*0.5), round(barSize*0.59*textScale*(self.settings["LegendRoundDataTo"]+len(str(round(lenth[1]))+units)))+10 + (8 if self.settings["LegendRoundDataTo"] != 0 else 0), 4), dtype=np.uint8)

            print(barSize*textScale, 'wad')
            imText = PIL.Image.fromarray(textLegend)
            drawText = PIL.ImageDraw.Draw(imText)

            font = PIL.ImageFont.truetype("arial.ttf", round(barSize*textScale))
            #font = PIL.ImageFont.load_default()
            #deez nutz
            MonocolorId = self.settings['MonocolorId']
            for i in range(steps):

                barsColor = None
                if Mode == 0:
                    val = round(255*(i/(steps-1)))

                    barsColor = np.array([val if MonocolorId[0] == 0 else MonocolorId[0], val if MonocolorId[1] == 0 else MonocolorId[1], val if MonocolorId[2] == 0 else MonocolorId[2], 255])
                    #print(barsColor, round(1.5*barSize*(steps-1-i)+barSize), round(1.5*barSize*(steps-1-i)), i/(steps-1), agenda.shape)
                elif Mode == 1:
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

                drawText.text((0,round(1.5*barSize*(steps-1-i)+((barSize-(barSize*textScale))/2))), " "+str(round((i/(steps-1))*(lenth[1]-lenth[0])+lenth[0], self.settings["LegendRoundDataTo"]))+units, font=font)

            textLegend = np.array(imText)
            AgendaObj = np.concatenate((Legend, textLegend), axis=1, dtype=np.uint8)
            #AgendaObj = CreateLegend((l, m), settings["Mode"], image.size, legendScale, legendSteps,  legendTextScale, legendRoundDataTo, legendUnits)
            #print(np.zeros((round((image.size[1]-AgendaObj.shape[0])*legendVerticalAlignment),  AgendaObj.shape[1], 4)).shape, AgendaObj.shape, np.zeros((round((image.size[1]-AgendaObj.shape[0])*(1-legendVerticalAlignment)),  AgendaObj.shape[1], 4)).shape,(image.size[1]-AgendaObj.shape[0])*legendVerticalAlignment, image.size[0])
            AgendaObj = np.concatenate( ( np.zeros((round((image.size[1]-AgendaObj.shape[0])*self.settings["LegendVerticalAlignment"]),  AgendaObj.shape[1], 4), dtype = np.uint8),\
            AgendaObj, np.zeros((image.size[1] - round((image.size[1]-AgendaObj.shape[0])*self.settings["LegendVerticalAlignment"]+AgendaObj.shape[0]),  AgendaObj.shape[1], 4),  dtype = np.uint8)))

            if self.settings["LegendHorizontalAlignment"].lower() == 'left':
                res = np.concatenate((AgendaObj, np.zeros((AgendaObj.shape[0], self.settings["LegendOffsetFromMap"], 4)), res), axis = 1)
            else:
                res = np.concatenate((res,np.zeros((AgendaObj.shape[0], self.settings["LegendOffsetFromMap"], 4)), AgendaObj), axis = 1)
        #print(res)
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

    t = time.time()
    #cpuArr = InterpolateRandomCpu(mapData)
    print(time.time()-t)
    arr = Interpolate(mapData)
    PIL.Image.fromarray(arr).show()


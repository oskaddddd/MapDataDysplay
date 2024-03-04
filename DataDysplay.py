#from tkinter import *
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
import time
import Interpolation
import ReadSettings
import QuadTree
import math



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
    #print(data)
    if data == None:
        #Read the data.json
        #print(data)
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
        self.settings = ReadSettings.Settings(True)
        self.image = PIL.Image.open(self.settings['image_name'])
        
        
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

        mode = self.settings["mode"]
        valueRange = None
        output = None
        
        
        
        #Gpu computation
        if self.settings["computation"].lower() == 'opencl':
            #IDW interpolation on the gpu
            if self.settings["interpolation"].lower() == 'idw':
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
            
            creator = Interpolation.interpolate_delauny_cpu(self.points, self.image, mode, None, self.settings['MonocolorId'], True)
            #creator.visualizeTriangles()
            o = creator.Interpolate()
            output = o[0]
            valueRange = (o[2], o[1])



    
        return output.astype(np.uint8)
    def CreateLegend(self, maxMin):
        numSections = self.settings['sections']
        legendHeight = self.image.size[1]
        sectionSize = 1
        legend_padding = 0
        sectionHeight = (legendHeight*self.settings['scale']) / (numSections/sectionSize)
        
        font_size = int(sectionHeight * self.settings['text_scale'])
        font = PIL.ImageFont.truetype("arial.ttf", font_size)
        roundTo = self.settings['round_to']
        
        maxTextWidth = [f'{f"%0.{roundTo}f"%maxMin[0]} {self.settings["units"]}',\
                        f'{f"%0.{roundTo}f"%maxMin[1]} {self.settings["units"]}']
        if len(maxTextWidth[0]) > len(maxTextWidth[1]): maxTextWidth = maxTextWidth[0]
        else: maxTextWidth = maxTextWidth[1]
        
        
        # Create a new image for the legend
        legend_image = PIL.Image.new("RGB", (10, legendHeight), color="white")
        draw = PIL.ImageDraw.Draw(legend_image)
        legendWidth = math.ceil(draw.textlength(maxTextWidth, font))
        
        legend_image = legend_image.resize((legendWidth, legendHeight))
        draw = PIL.ImageDraw.Draw(legend_image)
        print(legendWidth)
        # Draw sections with values and units
        for i in range(numSections):
            y_top = legend_padding + i * sectionHeight
            y_bottom = y_top + sectionHeight
            
            value = i * 255/numSections
            value_text = f'{f"%0.{roundTo}f"%value} {self.settings["units"]}'
            draw.rectangle([(0, y_top), (legendWidth, y_bottom)], outline="black", fill='red')
            draw.text((legend_padding, y_top), value_text, fill="black", font=font)

        # Calculate position based on vertical alignment
        y_position = int((self.image.size[1] - legend_image.size[1]) * self.settings['vertical_position'])

        legend_image.show()

        return self.image
        

if __name__ == "__main__":
    magic = create_map()
    #magic.DecodeData()
    magic.ReadData()
    t = time.time()
    image = magic.CreateLegend((-225, 255))
    print('speed:', time.time()-t)
    
    PIL.Image.fromarray(image).show()


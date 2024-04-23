#from tkinter import *
import PIL.Image, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
import time
import Interpolation
import ReadSettings
import QuadTree
import math
from Gradient import gradient



def prepare_data(data = None):
    #calibration
    cali = []
    
    #Get calibration data
    try:
        cali = ReadSettings.Settings()['calibrate']
        if cali == [[[0, 0], 0], [[0, 0], 0]]:
            exit()
    except Exception as e:
        print('Please set 2 calibration coordinates in Calibration.py\n', e)
        exit()
        
    #Calculate the decoding values
    cali[0]['gps'].reverse()
    cali[1]['gps'].reverse()
    k = [(cali[0]['pixel'][0]-cali[1]['pixel'][0])/(cali[0]['gps'][0]-cali[1]['gps'][0]),
        (cali[0]['pixel'][1]-cali[1]['pixel'][1])/(cali[0]['gps'][1]-cali[1]['gps'][1])]
    
    b = [cali[0]['pixel'][0]-(k[0]*cali[0]['gps'][0]),
        cali[0]['pixel'][1]-(k[1]*cali[0]['gps'][1])]
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
        n = [round(point["gps"][1]*k[0]+b[0]), round(point["gps"][0]*k[1]+b[1])]
        points[i] = np.array([n[0], n[1], point["value"]])
    
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
        if self.settings['manual_max_min']:
            self.maxMin = (self.settings['min'], self.settings['max'])
        
        
        
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
        self.maxMin = None
        output = None
        
        self.pointValues = self.points[:, 2]
        
        if not self.settings["manual_max_min"]:
            self.maxMin = (math.floor(min(self.pointValues)), math.ceil(max(self.pointValues)))
        else:
            self.maxMin = (self.settings["min"], self.settings["max"])
        
        #Gpu computation
        if self.settings["computation"].lower() == 'opencl':
            #IDW interpolation on the gpu
            if self.settings["interpolation"].lower() == 'idw':
                pass
                
            
            #Delauny triangulation on the gpu
            else:
                #Do the interpolation
                creator = Interpolation.interpolate_delauny_gpu(self.points, self.image, self.maxMin, self.settings['gradient'], True,True)
                creator.CreateBuffers()
                output = creator.Compute()  
                
        #Delauny interpolation on the cpu 
        else:
            
            creator = Interpolation.interpolate_delauny_cpu(self.points, self.image, self.maxMin, clip = True)
            #creator.visualizeTriangles()
            o = creator.Interpolate()
            output = o[0]
            self.maxMin = (o[2], o[1])


        if self.settings['create_legend']:
            output = self.CreateLegend(PIL.Image.fromarray(output.astype(np.uint8)))
            return output
        else:
            return PIL.Image.fromarray(output.astype(np.uint8))
    
    def CreateLegend(self, image):
        #Read and calculate all the variables from settings 
        numSections = self.settings['sections']
        
        barScale = self.settings['bar_scale']
         
        legendHeight = self.image.size[1]
        sectionHeight = (legendHeight*self.settings['scale']) / (numSections-(1-barScale))
        sectionWidth = self.settings["bar_width"]*sectionHeight*barScale
        
        verticalPosition = 1 - self.settings['vertical_position']
        verticalOffset = (1-self.settings['scale'])*verticalPosition*legendHeight
        
        font_size = int(sectionHeight * self.settings['text_scale']*barScale)
        font = PIL.ImageFont.truetype("arial.ttf", font_size)
        
        roundTo = self.settings['round_to']
        
        #Find the longest posible text
        longestText = [f'{f"%0.{roundTo}f"%self.maxMin[0]} {self.settings["units"]}',\
                       f'{f"%0.{roundTo}f"%self.maxMin[1]} {self.settings["units"]}']
        
        if len(longestText[0]) > len(longestText[1]): longestText = longestText[0]
        else: longestText = longestText[1]
        
        
        #Find the width of the legend based on the longest text
        legendWidth = math.ceil(font.getlength(longestText)+sectionWidth)
        
        #Calculate the offset of the text from the height of the bars
        textOffset = math.ceil(sectionHeight*barScale/5)
        
        #Create the legend image and the draw object
        legendImage = PIL.Image.new("RGBA", (self.image.size[0] + legendWidth+textOffset + self.settings['offset'], legendHeight), color=(0,0,0,0))
        draw = PIL.ImageDraw.Draw(legendImage)
        
        #load the gradient
        grad = gradient(self.maxMin, self.settings['gradient'])
        
        sectionValue = (self.maxMin[1] - self.maxMin[0])/(numSections-1)
        
        # Draw sections with values and units
        for i in range(numSections):
            value = self.maxMin[0]+i*sectionValue
            
            #Get the text for this section
            value_text = f'{f"%0.{roundTo}f"%value} {self.settings["units"]}'
            
            color = (*grad.GetColorAtPoint(value), 255)
            
            #Calculate the boundries of the bar
            yTop = 0
            yBottom = 0
            if i == 0:
                yTop = sectionHeight*barScale
                yBottom = 0
            else:
                yBottom = sectionHeight*i
                yTop = sectionHeight*barScale+yBottom
                
            yTop += verticalOffset
            yBottom += verticalOffset
            
            #Draw the bar and the text next to it
            xStart = 0 if self.settings['horizontal_alignment'] == 'left' else self.image.size[0] + self.settings['offset']
            draw.rectangle([(xStart, yBottom), (sectionWidth+xStart, yTop)], fill=color)
            draw.text((sectionWidth+textOffset+xStart, yBottom), value_text, fill="white", font=font)

            if self.settings['horizontal_alignment'] == 'left':
                legendImage.paste(image, (legendWidth+textOffset+ self.settings['offset'], 0))
            else:
                legendImage.paste(image, (0, 0))

        return legendImage
        

if __name__ == "__main__":
    magic = create_map()
    #magic.DecodeData()
    magic.ReadData()
    
    t = time.time()
    image = magic.Interpolate()
    print('speed:', time.time()-t)
    
    image.show()


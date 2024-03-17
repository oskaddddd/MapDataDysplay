from PyQt6.QtWidgets import *
from PyQt6 import uic
from PyQt6.QtCore import QTimer, QPointF, Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor

import sys
import qdarktheme
from ReadSettings import *
from DataDysplay import *

import time

import PIL.Image
settings = Settings()

class ClickableGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()


    def mousePressEvent(self, event):
        print("Mouse press event occurred on the red ellipse")
                

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('UI/UI.ui', self)
        
        self.map_scene = QGraphicsScene()
        self.map_viewer.setScene(self.map_scene)
        self.output = None
        
        
        self.mask_setup_scene = QGraphicsScene()
        self.mask_setup_viewer.setScene(self.mask_setup_scene)
        self.mask_setup_image = None
        self.mask_setup_array_unchenged = None
        self.mask_setup_array = None
        self.mask_image = PIL.Image.open("mask.png")
        
        self.calibrate_scene = QGraphicsScene()
        self.load_image(self.mask_image, self.calibrate_scene)
        self.calibrate_viewer.setScene(self.calibrate_scene)
        
        self.dot_pos = None
        
        
        
    

        ##########
        #SETTINGS#
        ##########

        #LOAD SETTINGS
        ##Mode
        self.mode_dropdown.setCurrentText(['Monocolor', 'RGB'][settings['mode']])
        ##Computation
        self.computation_dropdown.setCurrentText(['GPU', 'CPU'][['opencl', 'cpu'].index(settings['computation'])])
        ##Interpolation
        self.interpolation_dropdown.setCurrentText(['Delauny triangulation', 'IDW'][['delauny', 'idw'].index(settings['interpolation'])])
        ##Max min check
        self.manual_max_min_check.setChecked(settings['manual_max_min'])
        ##Max
        self.max_input.setValue(settings['max'])
        ##Min
        self.min_input.setValue(settings['min'])
        ##Create legend
        self.create_legend_check.setChecked(settings['create_legend'])
        #Horizontal alignment
        self.horizontal_alignment_dropdown.setCurrentText(['Right', 'Left'][['right', 'left'].index(settings['horizontal_alignment'])])
        #Vertical position
        self.vertical_position_slider.setValue(int(settings["vertical_position"]*100))
        #Scale   
        self.scale_slider.setValue(int(settings["scale"]*100))
        #Text scale
        self.text_scale_slider.setValue(int(settings["text_scale"]*100))
        ##Offset
        self.offset_input.setValue(settings['offset'])
        ##sections
        self.sections_input.setValue(settings['sections'])
        ##Units
        self.units_input.setText(settings['units'])
        ##Round To
        self.round_to_input.setValue(settings['round_to'])

        #Save Settings
        self.save_settings_button.clicked.connect(lambda: WriteSettings(settings))


        #CONNECT GENERAL SETTINGS
        ##Mode
        self.mode_dropdown.currentIndexChanged.connect(lambda data: self.change_setting(data, 'mode'))
        ##Computation
        self.computation_dropdown.currentIndexChanged.connect(lambda data: self.change_setting(['opencl', 'cpu'][data], 'computation'))        
        ##Interpolation
        self.interpolation_dropdown.currentIndexChanged.connect(lambda data: self.change_setting(['delauny', 'idw'][data], 'interpolation'))  
        ##Manual Max Min
        self.manual_max_min_check.stateChanged.connect(lambda data: self.change_setting(data==2, 'manual_max_min'))       
        ##Max
        self.max_input.valueChanged.connect(lambda data: self.change_setting(data, 'max'))
        ##Min
        self.min_input.valueChanged.connect(lambda data: self.change_setting(data, 'min'))


        #CONNECT LEGEND SETTINGS
        ##Create legend
        self.create_legend_check.stateChanged.connect(lambda data: self.change_setting(data==2, 'create_legend'))      
        ##Horizontal alignment
        self.horizontal_alignment_dropdown.currentIndexChanged.connect(lambda data: self.change_setting(['right', 'left'][data], 'horizontal_alignment'))
        ##Vertical position
        self.vertical_position_slider.valueChanged.connect(lambda data: self.change_setting(data/100, 'vertical_position'))
        ##Scale
        self.scale_slider.valueChanged.connect(lambda data: self.change_setting(data/100, 'scale'))
        ##Text scale
        self.text_scale_slider.valueChanged.connect(lambda data: self.change_setting(data/100, 'text_scale'))
        ##Offset
        self.offset_input.valueChanged.connect(lambda data: self.change_setting(data, 'offset'))
        ##Sections
        self.sections_input.valueChanged.connect(lambda data: self.change_setting(data, 'sections'))
        ##Units
        self.units_input.textChanged.connect(lambda data: self.change_setting(data, 'units'))
        ##Round to
        self.round_to_input.valueChanged.connect(lambda data: self.change_setting(data, 'round_to'))

        
        #SETUP
        #Load mask image button
        self.select_map_image_button.clicked.connect(self.load_mask_setup_image)
        #Save mask
        self.save_mask_image_button.clicked.connect(self.save_mask)
        #Update mask
        self.mask_threashold_slider.valueChanged.connect(lambda data: self.update_mask(data*7.65))
        
        #CALIBRATION
        self.calibrate_point_button.clicked.connect(self.point_button)
        
        self.calibrate_gps1_input.valueChanged.connect(lambda value: self.update_calibration_settings('gps', 0, value))
        self.calibrate_gps2_input.valueChanged.connect(lambda value: self.update_calibration_settings('gps', 1, value))
     
        #Load data button
        self.load_data_button.clicked.connect(self.prepare_data)
        #Create Button
        self.create_button.clicked.connect(self.create_image)
        #Save image
        self.save_image_button.clicked.connect(lambda: self.save_image(self.output))
        self.show()
        
        self.error_message_timer = QTimer()
        self.error_message_timer.timeout.connect(lambda: self.error_message.setText(''))
        

    #CALIBRATION
    def point_button(self):
        self.calibrate_point_index = 0 if self.calibrate_point_button.isChecked() == False else 1
        self.calibrate_point_button.setText(f'Point {self.calibrate_point_index+1}')
        
        self.calibrate_gps1_input.setValue(settings['calibrate'][self.calibrate_point_index]["gps"][0])
        self.calibrate_gps2_input.setValue(settings['calibrate'][self.calibrate_point_index]["gps"][1])
        
        print(self.calibrate_point_index, self.calibrate_point_button.isChecked())
    
    def update_calibration_settings(self, setting, coordinate_index, value):
        settings['calibrate'][self.calibrate_point_index][setting][coordinate_index] = value
        print(value)
    #MASK CREATION
    def save_mask(self):
        self.mask_image = self.mask_setup_image
        self.load_image(self.mask_image, self.calibrate_scene)
        self.save_image(self.mask_setup_image, "mask.png")
        
    def update_mask(self, threashold):
        inverse = True
        
        #Check if any mask image is loaded
        if type(self.mask_setup_array) != np.ndarray:
            return
        
        #Checks if the threashold is invered   
        if threashold < 0:
            inverse = False
        
        #Reset threashold
        threashold = abs(threashold)
        
        #Calculate the mask according to the threashold
        mask = None
        if inverse:
            mask = np.sum(self.mask_setup_array_unchenged, axis=2) < threashold
        else:
            mask = np.sum(self.mask_setup_array_unchenged, axis=2) > threashold
        
        #Update the mask image according to the newly created mask     
        self.mask_setup_array[:, :, :] = 255
        self.mask_setup_array[mask, 3] = 0
        print(threashold, inverse)
        self.mask_setup_image = PIL.Image.fromarray(self.mask_setup_array)
        
        #Dysplay the image on screen
        self.load_image(self.mask_setup_image, self.mask_setup_scene)
                
    
    def load_mask_setup_image(self):
        #Load the mask image to screen
        path = self.select_file("Images (*.png)", "Select map image", 'open')
        if path != None:
            self.mask_setup_image = PIL.Image.open(path)
            self.mask_setup_array_unchenged = np.array(self.mask_setup_image)
            self.mask_setup_array = self.mask_setup_array_unchenged.copy()
            self.load_image(self.mask_setup_image, self.mask_setup_scene)
            
    #SETTINGS PAGE    
    def change_setting(self, data, setting):
        print(data)
        settings[setting] = data
        
        
    #MAIN IMAGE CREATION SCREEN       
    def create_image(self):

        t = time.time()
        #Load the data
        mapObj = create_map()
        e = mapObj.ReadData()
        if e != None:
            self.error_message.setText(e)
            return
        
        #Create the map image
        self.output = mapObj.Interpolate()
        print('speed:', time.time()-t)
        
        self.load_image(self.output, self.map_scene)

        
    def prepare_data(self):
        file = self.select_file("All (*);;Json files (*.json)", "Select data file", 'open')
        if file == None: return
        data  = []
        with open(file, 'r') as f:
            data = json.load(f)
        prepare_data(data)
        
        
    #UNIVERSAL FUNCTIONS
    def load_image(self, image, scene):
        qImage = QImage(image.tobytes(), image.size[0], image.size[1], QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qImage)
        
        scene.clear()
        scene.addPixmap(pixmap)
        
    
    def select_file(self, fileType, message, action, forceFileType = None):
        print(fileType)
        
        if action == 'open':
            fileName, _ = QFileDialog.getOpenFileName(self, message, "", fileType, options=QFileDialog.Option(1))
            print(fileName)
            if fileName:
                return fileName
        elif action == 'save':
            fileName, _ = QFileDialog.getSaveFileName(None, message, "", fileType)
            
            if fileName:
                if forceFileType != None and not fileName.endswith(forceFileType):
                    fileName+=forceFileType
                print(fileName)
                return fileName    
            
              
    def save_image(self, image, path = None):
        if image == None:
            self.error_message.setText('Please create the image before saving it')
            self.error_message_timer.start(3000)
            return
        if path == None:
            path = self.select_file("Images (*.png)", "Save image", 'save', '.png')
            if path == None:
                return
        print(path)
        image.save(path)      
    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    qdarktheme.setup_theme()
    
    window = Ui()
    app.exec()
    

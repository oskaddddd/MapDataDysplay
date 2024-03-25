from PyQt6.QtWidgets import *
from PyQt6 import uic
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QImage, QColor, QBrush

import sys
import qdarktheme
from ReadSettings import *
from DataDysplay import *

import time

import PIL.Image
settings = Settings()

class ClickableGraphicsView(QGraphicsView):
    clicked = pyqtSignal(tuple)
    

    
    def __init__(self, parent=None):
        super().__init__(parent)
        print('HAHA')


    def mousePressEvent(self, event):
        #print("Mouse press event occurred on the red ellipse")
        item = self.itemAt(event.pos())
        print('click')
        # Check if the item is not None and is the image item
        if isinstance(item, QGraphicsPixmapItem):
            print("Clicked on the image")
            self.clicked.emit((event.pos().x(), event.pos().y()))


                

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
        
        
        print(self.calibrate_viewer)
        #self.calibrate_viewer = ClickableGraphicsView()
        self.calibrate_scene = QGraphicsScene()
        self.load_image(self.mask_image, self.calibrate_scene)
        self.calibrate_viewer.setScene(self.calibrate_scene)
        
        print(self.calibrate_viewer)
        self.calibrate_selector_dot = None
        self.calibrate_dot_coordinates = [settings['calibrate'][0]["pixel"], settings['calibrate'][1]["pixel"]]
        self.calibrate_gps = [settings['calibrate'][0]["gps"], settings['calibrate'][1]["gps"]]
        
        self.point_button()

        
        
        
    

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
        
        self.calibrate_gps1_input.valueChanged.connect(lambda value: self.change_gps_value(value, 0))
        self.calibrate_gps2_input.valueChanged.connect(lambda value: self.change_gps_value(value, 1))

        self.calibrate_viewer.clicked.connect(lambda coordinates: self.image_click(coordinates))
        
        self.calibrate_save_button
        
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
    def save_calibration(self):
        settings['calibrate'][0]['gps'] = self.calibrate_gps[0]
        settings['calibrate'][1]['gps'] = self.calibrate_gps[1]
        settings['calibrate'][0]['pixel'] = self.calibrate_dot_coordinates[0]
        settings['calibrate'][1]['pixel'] = self.calibrate_dot_coordinates[1]
        
        WriteSettings(settings)
        
    def change_gps_value(self, value, index):
        print(value, index)
        self.calibrate_gps[index] = value
        
    def point_button(self):
        self.calibrate_point_index = 0 if self.calibrate_point_button.isChecked() == False else 1
        self.calibrate_point_button.setText(f'Point {self.calibrate_point_index+1}')
        
        self.calibrate_gps1_input.setValue(settings['calibrate'][self.calibrate_point_index]["gps"][0])
        self.calibrate_gps2_input.setValue(settings['calibrate'][self.calibrate_point_index]["gps"][1])
        
        self.image_click(self.calibrate_dot_coordinates[self.calibrate_point_index], True)
        
        print(self.calibrate_point_index, self.calibrate_point_button.isChecked())
    
        
    def image_click(self, coordinates, image = False):
        print(coordinates)
        
        color = QColor(Qt.GlobalColor.red)
        dot_size = 4
        coordinates = [int(coordinates[0]), int(coordinates[1])]
        if image:
            if self.calibrate_selector_dot:
                self.calibrate_scene.removeItem(self.calibrate_selector_dot)
            
            #Convert scene coordinates to image coordinates
            image_x = coordinates[0] * self.mask_image.size[0] / self.calibrate_viewer.width()
            image_y = coordinates[1] * self.mask_image.size[1] / self.calibrate_viewer.height()
            
            #Draw the filled dot on the scene at the image coordinates
            self.calibrate_selector_dot = self.calibrate_scene.addEllipse(coordinates[0] - dot_size / 2, coordinates[1] - dot_size / 2, dot_size, dot_size, brush=QBrush(color))
            
            #Convert click coordinates to scene coordinates
            scene_pos = self.calibrate_viewer.mapToScene(coordinates[0], coordinates[1])
            
            #Get the item at the scene coordinates
            item = self.calibrate_viewer.scene().itemAt(scene_pos, self.calibrate_viewer.transform())
            print(item)
        else:
            scene_pos = self.calibrate_viewer.mapToScene(coordinates[0], coordinates[1])

            # Get the item at the scene coordinates
            item = self.calibrate_viewer.scene().itemAt(scene_pos, self.calibrate_viewer.transform())
            print(item)
            if isinstance(item, QGraphicsPixmapItem) or isinstance(item, QGraphicsEllipseItem):
                print('YES')
                #Convert scene coordinates to local coordinates of the image
                image_pos = item.mapFromScene(scene_pos)

                x = image_pos.x()
                y = image_pos.y()
                #Print the local coordinates of the image
                print("Clicked on the image at position:", x, y)

                if self.calibrate_selector_dot:
                    self.calibrate_scene.removeItem(self.calibrate_selector_dot)
                self.calibrate_selector_dot = self.calibrate_scene.addEllipse(x - dot_size / 2, y - dot_size / 2, dot_size, dot_size, brush=QBrush(color))
                self.calibrate_dot_coordinates[self.calibrate_point_index] = [x, y]

    
    #MASK CREATION
    def save_mask(self):
        self.mask_image = self.mask_setup_image
        self.mask_image.convert('1')
        test = np.array(self.mask_image)
        print(test[300][200])
        
        self.load_image(self.mask_image, self.calibrate_scene)
        self.save_image(self.mask_image, "mask.png")
        
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
        self.mask_setup_array[mask, :] = 0
        #print(self.mask_setup_array)
        print(threashold, inverse)
        self.mask_setup_image = PIL.Image.fromarray(self.mask_setup_array)
        
        #Dysplay the image on screen
        self.load_image(self.mask_setup_image, self.mask_setup_scene)
                
    
    def load_mask_setup_image(self):
        #Load the mask image to screen
        path = self.select_file("Images (*.png)", "Select map image", 'open')
        if path != None:
            self.mask_setup_image = PIL.Image.open(path).convert('RGBA')
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
        for item in scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                scene.removeItem(item)
        scene.addPixmap(pixmap)
        scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
        
    
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
    

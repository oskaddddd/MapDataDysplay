from PyQt5.QtWidgets import *
from PyQt5 import uic, QtCore

import sys
import qdarktheme
from ReadSettings import *
settings = Settings()

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('UI/UI.ui', self)
        

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


        self.show()
    

    def change_setting(self, data, setting):
        print(data)
        settings[setting] = data
        

app = QApplication(sys.argv)
app.setStyle('Fusion')
qdarktheme.setup_theme()
window = Ui()
app.exec_()

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
        self.show()
        
        #Connect the create legend checkmark
        self.create_legend_check.stateChanged.connect(self.legend_settings.setEnabled)
        self.create_legend_check.stateChanged.connect(settings['create_legend'])
        self.create_legend_check.stateChanged.connect(self.test)
    
    def test(self):
        print(settings['create_legend'])
        
        

app = QApplication(sys.argv)
app.setStyle('Fusion')
qdarktheme.setup_theme()
window = Ui()
app.exec_()

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

class GradientSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.colors = [QColor(255, 0, 0), QColor(0, 0, 255)]  # Initial gradient colors

    def initUI(self):
        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle('Gradient Selector')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the gradient
        gradient = QPainter(self)
        gradient.begin(self)
        gradient.setBrush(Qt.LinearGradient(self.rect().topLeft(), self.rect().topRight()))
        gradient.setPen(Qt.NoPen)
        gradient.setColorAt(0, self.colors[0])
        gradient.setColorAt(1, self.colors[1])
        gradient.drawRect(self.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x()
            color_index = x / self.width()
            if color_index < 0:
                color_index = 0
            elif color_index > 1:
                color_index = 1
            color = QColorDialog.getColor()
            self.colors[int(color_index * 2)] = color
            self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GradientSelector()
    ex.show()
    sys.exit(app.exec_())
import sys
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PyQt6.QtGui import QPixmap, QImage

def main():
    # Create the application
    app = QApplication(sys.argv)

    # Create a QGraphicsView and QGraphicsScene
    view = QGraphicsView()
    scene = QGraphicsScene()
    
    # Load the image
    image_path = "/home/oskaras/Documents/Programing/MapDataDysplay/mask1.png"
    image = QImage(image_path)
    pixmap = QPixmap.fromImage(image)

    # Create a QGraphicsPixmapItem to display the image
    pixmap_item = scene.addPixmap(pixmap)

    # Set the scene to the view
    view.setScene(scene)

    # Show the QGraphicsView
    view.show()

    # Execute the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
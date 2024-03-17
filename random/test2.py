import sys
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QGraphicsItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter


class ClickableImageView:
    def __init__(self, graphics_view):
        self.graphics_view = graphics_view
        self.graphics_view.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.graphics_view:
            if event.type() == Qt.EventType.MouseButtonPress:
                if obj.scene().itemAt(obj.mapToScene(event.pos()), obj.transform()) is not None:
                    print("Clicked on the image")
        return False


def main():
    app = QApplication(sys.argv)
    viewer = QGraphicsView()
    scene = QGraphicsScene()
    viewer.setScene(scene)
    viewer.setRenderHint(QPainter.RenderHint.Antialiasing)  # Optional: for better image quality
    image_item = scene.addPixmap(QPixmap("image.jpg"))  # Load your image here
    image_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)

    clickable_image_view = ClickableImageView(viewer)

    viewer.resize(600, 400)
    viewer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
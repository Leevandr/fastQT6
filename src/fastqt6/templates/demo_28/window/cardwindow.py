from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget

from py_ui.card import Ui_Form


class CardWindow(QWidget, Ui_Form):
    clicked = pyqtSignal(dict)

    def __init__(self, product):
        super().__init__()
        self.product = product
        self.setupUi(self)
        self.load_product()

    def load_product(self):
        self.label_name.setText(self.product["description"])
        self.label_price.setText(str(self.product["price"]))
        self.label_brand.setText(str(self.product["quantity"]))
        if self.product["image"]:
            image_path = "image/" + self.product["image"]
            pixmap = QPixmap(image_path).scaled(100, 100)
            self.label_image.setPixmap(pixmap)

    def mousePressEvent(self, a0):
        self.clicked.emit(self.product)

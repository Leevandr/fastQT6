from PyQt6.QtWidgets import QDialog, QFileDialog

from py_ui.dialog import Ui_Dialog


class DialogWindow(QDialog, Ui_Dialog):
    def __init__(self, order: dict | None = None):
        super().__init__()
        self.setupUi(self)
        self.order = order
        self.load_order()
        self.pushButton_load.clicked.connect(self.load_image)
        self.pushButton_save.clicked.connect(self.accept)

    def load_order(self):
        if self.order is None:
            return
        self.nameLineEdit.setText(self.order["description"])
        self.brandLineEdit.setText(str(self.order["quantity"]))
        self.priceLineEdit.setText(str(self.order["price"]))
        self.imageLineEdit.setText(self.order["image"] or "")

    def get_order(self):
        description = self.nameLineEdit.text()
        quantity = self.brandLineEdit.text()
        price = self.priceLineEdit.text()
        image = self.imageLineEdit.text()
        return description, price, quantity, image

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите фото", "image/", "All Files (*)")
        if path:
            self.imageLineEdit.setText(path.split("/")[-1])

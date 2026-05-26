from PyQt6.QtWidgets import QWidget

from ui.gen.ItemOrderWidget import Ui_ItemOrderWidget


class ItemOrderWidget(QWidget):
    def __init__(self, item):
        super().__init__()
        self.ui = Ui_ItemOrderWidget()
        self.ui.setupUi(self)

        self.item = item
        self.is_selected = False
        self.fill()

    def apply_style(self):
        self.setProperty("selected", self.is_selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_selected(self, value: bool):
        self.is_selected = value
        self.apply_style()

    def fill(self):
        self.apply_style()
        self.ui.label_status_name.setText(f'Статус: {self.item["status"]}')
        self.ui.label_product_name.setText(f'Артикул: {self.item["article"]}')
        self.ui.label_pickup_point.setText(f'Пункт выдачи: {self.item["pickup"]}')
        self.ui.label_order_date.setText(f'Дата заказа: {self.item["order_date"]}')
        self.ui.label_delivery_date.setText(f'Дата выдачи: {self.item["delivery_date"]}')

    def mousePressEvent(self, a0):
        main = self.window()
        main.select_widget(self)

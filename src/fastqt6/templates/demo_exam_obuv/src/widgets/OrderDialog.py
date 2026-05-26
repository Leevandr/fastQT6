from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QDialog

from src.db import dao
from ui.gen.OrderDialog import Ui_OrderDialog


class OrderDialog(QDialog):
    def __init__(self, item=None, user=None):
        super().__init__()
        self.ui = Ui_OrderDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Заказ")
        self.translate_labels()

        self.item = item
        self.user = user
        self.fill()

        if self.item:
            self.fill_exist()

        self.ui.pushButton_save.clicked.connect(self.save)

    def translate_labels(self):
        self.ui.productLabel.setText("Артикул")
        self.ui.statusLabel.setText("Статус")
        self.ui.pickupLabel.setText("Пункт выдачи")
        self.ui.orderLabel.setText("Дата заказа")
        self.ui.deliveryLabel.setText("Дата выдачи")

    def fill(self):
        products = dao.get_all_products()
        for product in products:
            title = f'{product["article"]} - {product["title"]}'
            self.ui.productComboBox.addItem(title, product["id"])

        statuses = dao.get_all_statuses()
        for status in statuses:
            self.ui.statusComboBox.addItem(status["title"], status["id"])

        points = dao.get_all_pickup_points()
        for point in points:
            self.ui.pickupComboBox.addItem(point["address"], point["id"])

        self.ui.orderDateEdit.setCalendarPopup(True)
        self.ui.deliveryDateEdit.setCalendarPopup(True)
        self.ui.orderDateEdit.setDate(QDate.currentDate())
        self.ui.deliveryDateEdit.setDate(QDate.currentDate())

    def set_combo_by_data(self, combo, value):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def set_date(self, date_edit, value):
        text = str(value)
        date = QDate.fromString(text, "yyyy-MM-dd")
        if date.isValid():
            date_edit.setDate(date)

    def fill_exist(self):
        self.set_combo_by_data(self.ui.productComboBox, self.item["product_id"])
        self.set_combo_by_data(self.ui.statusComboBox, self.item["status_id"])
        self.set_combo_by_data(self.ui.pickupComboBox, self.item["pickup_point_id"])
        self.set_date(self.ui.orderDateEdit, self.item["order_date"])
        self.set_date(self.ui.deliveryDateEdit, self.item["delivery_date"])

    def save(self):
        product_id = self.ui.productComboBox.currentData()
        status_id = self.ui.statusComboBox.currentData()
        pickup_id = self.ui.pickupComboBox.currentData()
        order_date = self.ui.orderDateEdit.date().toString("yyyy-MM-dd")
        delivery_date = self.ui.deliveryDateEdit.date().toString("yyyy-MM-dd")

        if self.item:
            user_id = self.item["user_id"]
            dao.edit_order(self.item["id"], product_id, status_id, pickup_id, order_date, delivery_date, user_id)
        else:
            user_id = self.user["id"] if self.user else 1
            dao.add_order(product_id, status_id, pickup_id, order_date, delivery_date, user_id)

        self.accept()

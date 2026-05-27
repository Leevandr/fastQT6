from PyQt6.QtWidgets import QWidget, QDialog, QMessageBox, QTableWidgetItem

from database.db import dao
from py_ui.main import Ui_Form
from window.cardwindow import CardWindow
from window.dialogwindow import DialogWindow


class MainWindow(QWidget, Ui_Form):
    def __init__(self, account=None):
        super().__init__()
        self.account = account
        self.selected = None
        self.setupUi(self)

        self.pushButton_add.clicked.connect(self.add_product)
        self.pushButton_edit.clicked.connect(self.edit_product)
        self.pushButton_del.clicked.connect(self.del_product)

        if self.account is None:
            self.tabWidget.setTabVisible(1, False)
            self.pushButton_add.hide()
            self.pushButton_edit.hide()
            self.pushButton_del.hide()

        elif self.account["role_id"] == 1:
            self.tabWidget.setTabVisible(1, False)
            self.pushButton_add.hide()
            self.pushButton_edit.hide()
            self.pushButton_del.hide()

        elif self.account["role_id"] == 2:
            self.pushButton_add.hide()
            self.pushButton_edit.hide()
            self.pushButton_del.hide()

        self.comboBox.addItem("Все категории", None)
        for cat in dao.all_categories():
            self.comboBox.addItem(cat["name"], cat["id"])
        self.comboBox.currentIndexChanged.connect(self.table_widget)

        self.widget_product()
        self.table_widget()

    def widget_product(self):
        while self.verticalLayout_product.count():
            widget = self.verticalLayout_product.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()
        items = dao.all_product()
        for item in items:
            card = CardWindow(item)
            card.clicked.connect(self.click_product)
            self.verticalLayout_product.addWidget(card)

    def click_product(self, product):
        self.selected = product

    def add_product(self):
        dialog = DialogWindow()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            description, price, quantity, image = dialog.get_order()
            dao.add_product_bd(description, price, quantity, image)
            self.widget_product()

    def del_product(self):
        if self.selected is None:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return
        dao.delete_product(self.selected["id"])
        self.selected = None
        self.widget_product()

    def edit_product(self):
        if self.selected is None:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return
        dialog = DialogWindow(self.selected)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            description, price, quantity, image = dialog.get_order()
            dao.update_product(self.selected["id"], description, price, quantity, image)
            self.widget_product()

    def table_widget(self):
        category_id = self.comboBox.currentData()
        if category_id is None:
            self.info = dao.all_product()
        else:
            self.info = dao.products_by_category(category_id)
        self.tableWidget.setRowCount(len(self.info))
        for i in range(len(self.info)):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(str(self.info[i]["name"])))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(self.info[i]["description"])))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(str(self.info[i]["price"])))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str(self.info[i]["quantity"])))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(str(self.info[i]["image"])))

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QLayout, QMessageBox, QDialog

from src.db import dao
from src.widgets.ItemOrderWidget import ItemOrderWidget
from src.widgets.ItemDialog import ItemDialog
from src.widgets.ItemWidget import ItemWidget
from src.widgets.OrderDialog import OrderDialog
from ui.gen.MainWidget import Ui_MainWidget


ROOT_DIR = Path(__file__).resolve().parents[2]
IMAGES_DIR = ROOT_DIR / "resources" / "images"


def clear_layout(layout: QLayout):
    while layout.count():
        w = layout.takeAt(0).widget()
        if w:
            w.deleteLater()


class MainWindow(QWidget):
    def __init__(self, user=None):
        super().__init__()
        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)
        self.setWindowTitle("Магазин обуви")

        self.user = user
        self.selected_widget = None
        self.fill_logo()
        self.fill_fio()
        self.access_setting()
        self.fill_comboboxes()
        self.conn()
        self.add_widgets_items()
        self.add_widgets_orders()

    def conn(self):
        self.ui.pushButton_add_product.clicked.connect(self.add_product)
        self.ui.pushButton_edit_product.clicked.connect(self.edit_product)
        self.ui.pushButton_delete_product.clicked.connect(self.delete_product)
        self.ui.pushButton_logout.clicked.connect(self.logout)

        self.ui.lineEdit_search.textChanged.connect(self.add_widgets_items)
        self.ui.comboBox_quantity.currentIndexChanged.connect(self.add_widgets_items)
        self.ui.comboBox_suppilers.currentIndexChanged.connect(self.add_widgets_items)

        self.ui.pushButton_add_order.clicked.connect(self.add_order)
        self.ui.pushButton_edit_order.clicked.connect(self.edit_order)
        self.ui.pushButton_delete_order.clicked.connect(self.delete_order)

    def fill_logo(self):
        logo_path = IMAGES_DIR / "logo.png"
        icon_path = IMAGES_DIR / "app_icon.png"

        self.setWindowIcon(QIcon(str(icon_path)))
        self.ui.label_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            self.ui.label_logo.setPixmap(
                pixmap.scaled(
                    170,
                    52,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

    def delete_product(self):
        if self.selected_widget and isinstance(self.selected_widget, ItemWidget):
            result = QMessageBox.question(
                self,
                "Удаление товара",
                "Вы действительно хотите удалить товар?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.Yes:
                deleted = dao.delete_product(self.selected_widget.item["id"])
                if not deleted:
                    QMessageBox.warning(self, "Ошибка", "Товар есть в заказе, удалить нельзя")
                self.add_widgets_items()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")

    def fill_comboboxes(self):
        self.ui.comboBox_suppilers.addItem("Все поставщики")
        suppilers = dao.get_all_suppilers()
        for suppiler in suppilers:
            self.ui.comboBox_suppilers.addItem(suppiler["title"])

        self.ui.comboBox_suppilers.setCurrentText("Все поставщики")

        self.ui.comboBox_quantity.addItem("По умолчанию")
        self.ui.comboBox_quantity.addItem("По возрастанию")
        self.ui.comboBox_quantity.addItem("По убыванию")

    def select_widget(self, widget: QWidget):
        if self.selected_widget:
            self.selected_widget.set_selected(False)

        self.selected_widget = widget
        self.selected_widget.set_selected(True)

    def edit_product(self):
        if self.selected_widget and isinstance(self.selected_widget, ItemWidget):
            if ItemDialog(self.selected_widget.item).exec() == QDialog.DialogCode.Accepted:
                self.add_widgets_items()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите товар для редактирования")

    def add_product(self):
        if ItemDialog().exec() == QDialog.DialogCode.Accepted:
            self.add_widgets_items()

    def logout(self):
        from src.widgets.Auth import Auth

        self.auth_window = Auth()
        self.auth_window.show()
        self.close()

    def add_widgets_items(self):
        self.selected_widget = None

        clear_layout(self.ui.verticalLayout_products)

        search = self.ui.lineEdit_search.text()
        quantity = self.ui.comboBox_quantity.currentText()
        suppiler = self.ui.comboBox_suppilers.currentText()

        items = dao.get_all_products(search, quantity, suppiler)
        for item in items:
            self.ui.verticalLayout_products.addWidget(ItemWidget(item))

    def add_widgets_orders(self):
        self.selected_widget = None
        clear_layout(self.ui.verticalLayout_orders)
        orders = dao.get_all_orders()
        for order in orders:
            self.ui.verticalLayout_orders.addWidget(ItemOrderWidget(order))

    def add_order(self):
        if OrderDialog(user=self.user).exec() == QDialog.DialogCode.Accepted:
            self.add_widgets_orders()

    def edit_order(self):
        if self.selected_widget and isinstance(self.selected_widget, ItemOrderWidget):
            if OrderDialog(self.selected_widget.item, self.user).exec() == QDialog.DialogCode.Accepted:
                self.add_widgets_orders()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ")

    def delete_order(self):
        if self.selected_widget and isinstance(self.selected_widget, ItemOrderWidget):
            result = QMessageBox.question(
                self,
                "Удаление заказа",
                "Вы действительно хотите удалить заказ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.Yes:
                dao.delete_order(self.selected_widget.item["id"])
                self.add_widgets_orders()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите заказ")

    def access_setting(self):
        if self.user:
            role_id = self.user["role_id"]

            if role_id in (2, 3):
                self.ui.pushButton_add_product.setVisible(False)
                self.ui.pushButton_edit_product.setVisible(False)
                self.ui.pushButton_delete_product.setVisible(False)
                self.ui.pushButton_add_order.setVisible(False)
                self.ui.pushButton_edit_order.setVisible(False)
                self.ui.pushButton_delete_order.setVisible(False)
                self.ui.tabWidget.setTabVisible(1, False)
                self.ui.lineEdit_search.setVisible(False)
                self.ui.comboBox_quantity.setVisible(False)
                self.ui.comboBox_suppilers.setVisible(False)

            if role_id == 4:
                self.ui.pushButton_add_product.setVisible(False)
                self.ui.pushButton_edit_product.setVisible(False)
                self.ui.pushButton_delete_product.setVisible(False)
                self.ui.pushButton_add_order.setVisible(False)
                self.ui.pushButton_edit_order.setVisible(False)
                self.ui.pushButton_delete_order.setVisible(False)

        else:
            self.ui.pushButton_add_product.setVisible(False)
            self.ui.pushButton_edit_product.setVisible(False)
            self.ui.pushButton_delete_product.setVisible(False)
            self.ui.pushButton_add_order.setVisible(False)
            self.ui.pushButton_edit_order.setVisible(False)
            self.ui.pushButton_delete_order.setVisible(False)

            self.ui.tabWidget.setTabVisible(1, False)

            self.ui.lineEdit_search.setVisible(False)
            self.ui.comboBox_quantity.setVisible(False)
            self.ui.comboBox_suppilers.setVisible(False)

    def fill_fio(self):
        if self.user:
            self.ui.fio.setText(str(self.user["full_name"]))
        else:
            self.ui.fio.setText("Гостевой режим")

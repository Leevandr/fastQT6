import shutil
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox

from src.db import dao
from src.widgets.ItemWidget import image_path
from ui.gen.ItemDialog import Ui_ItemDialog


class ItemDialog(QDialog):
    def __init__(self, item=None):
        super().__init__()
        self.ui = Ui_ItemDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Товар")
        self.translate_labels()
        self.item = item
        self.image_name = "img.png"
        self.fill()
        if self.item:
            if self.item["image"] and self.item["image"] != "None":
                self.image_name = self.item["image"]
            self.fill_exist()

        self.ui.pushButton_save.clicked.connect(self.save)
        self.ui.pushButton_image.clicked.connect(self.choose_image)

    def translate_labels(self):
        self.ui.articleLabel.setText("Артикул")
        self.ui.titleLabel.setText("Название")
        self.ui.categoryLabel.setText("Категория")
        self.ui.descriptionLabel.setText("Описание")
        self.ui.manufactureLabel.setText("Производитель")
        self.ui.suppilerLabel.setText("Поставщик")
        self.ui.priceLabel.setText("Цена")
        self.ui.unitLabel.setText("Единица")
        self.ui.quantityLabel.setText("Количество")
        self.ui.discountLabel.setText("Скидка")
        self.ui.imageLabel.setText("Изображение")
        self.ui.label.setText("Изображение не выбрано")

    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать изображение",
            "",
            "Картинки (*.png *.jpg *.jpeg)"
        )
        if not file_path:
            return
        src = Path(file_path)

        project_dir = Path(__file__).resolve().parents[2]
        images_dir = project_dir / "resources" / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        dst = images_dir / src.name
        if src.resolve() != dst.resolve():
            pixmap = QPixmap(str(src))
            if pixmap.isNull():
                shutil.copy(src, dst)
            else:
                pixmap = pixmap.scaled(
                    300,
                    200,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                pixmap.save(str(dst))

        self.image_name = src.name

        pixmap = QPixmap(str(dst)).scaled(
            300,
            200,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.ui.label.setPixmap(pixmap)

    def delete_old_image(self, new_image):
        if not self.item:
            return

        old_image = self.item.get("image")
        if not old_image or old_image in ("None", "img.png") or old_image == new_image:
            return

        old_path = Path(image_path(old_image))
        try:
            if old_path.exists():
                old_path.unlink()
        except OSError:
            pass

    def fill_exist(self):
        item = self.item
        self.ui.categoryComboBox.setCurrentText(item["category"])
        self.ui.manufactureComboBox.setCurrentText(item["manufacture"])
        self.ui.suppilerComboBox.setCurrentText(item["suppiler"])
        self.ui.unitComboBox.setCurrentText(item["unit"])

        self.ui.spinBox.setValue(int(item["article"]) if str(item["article"]).isdigit() else 0)
        self.ui.titleLineEdit.setText(item["title"])
        self.ui.descriptionLineEdit.setText(item["description"])
        self.ui.priceSpinBox.setValue(int(item["price"]))
        self.ui.spinBox_quantity.setValue(int(item["quantity"]))
        self.ui.discountDoubleSpinBox.setValue(float(item["discount"]))

        image_name = self.image_name or "img.png"
        pixmap = QPixmap(image_path(image_name))
        if pixmap.isNull():
            pixmap = QPixmap(image_path("img.png"))

        pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio)
        self.ui.label.setPixmap(pixmap)


    def fill(self):
        categories = dao.get_all_categories()
        for category in categories:
            self.ui.categoryComboBox.addItem(category["title"])
        suppilers = dao.get_all_suppilers()
        for suppiler in suppilers:
            self.ui.suppilerComboBox.addItem(suppiler["title"])
        manufactures = dao.get_all_manufactures()
        for manufacture in manufactures:
            self.ui.manufactureComboBox.addItem(manufacture["title"])
        units = dao.get_all_units()
        for unit in units:
            self.ui.unitComboBox.addItem(unit["title"])

    def save(self):

        article = self.ui.spinBox.value()
        title = self.ui.titleLineEdit.text()
        description = self.ui.descriptionLineEdit.text()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Введите название товара")
            return

        category = self.ui.categoryComboBox.currentText()
        category_id = dao.get_category_id(category)["id"]

        manufacture = self.ui.manufactureComboBox.currentText()
        manufacture_id = dao.get_manufacture_id(manufacture)["id"]

        suppiler = self.ui.suppilerComboBox.currentText()
        suppiler_id = dao.get_suppiler_id(suppiler)["id"]

        unit = self.ui.unitComboBox.currentText()
        unit_id = dao.get_unit_id(unit)["id"]

        discount = self.ui.discountDoubleSpinBox.value()
        quantity = self.ui.spinBox_quantity.value()
        image = self.image_name or "img.png"
        price = self.ui.priceSpinBox.value()

        if self.item:
            product_id = self.item["id"]
            dao.edit_product(product_id,
                             str(article),
                             str(title),
                             str(category_id),
                             str(description),
                             str(manufacture_id),
                             str(suppiler_id),
                             str(price),
                             str(unit_id),
                             str(quantity),
                             str(discount),
                             str(image))
            self.delete_old_image(image)
        else:
            dao.add_new_product(str(article),
                                str(title),
                                str(category_id),
                                str(description),
                                str(manufacture_id),
                                str(suppiler_id),
                                str(price),
                                str(unit_id),
                                str(quantity),
                                str(discount),
                                str(image))

        self.accept()

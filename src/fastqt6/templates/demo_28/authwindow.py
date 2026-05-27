from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication

from database.db import dao
from py_ui.auth import Ui_Form
from window.mainwindow import MainWindow


class AuthWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.window = None
        self.pushButton_user.clicked.connect(self.user_login)
        self.pushButton_guest.clicked.connect(self.guest_login)

    def user_login(self):
        login = self.lineEdit_login.text()
        password = self.lineEdit_pass.text()
        account = dao.login_user(login, password)
        if account is None:
            QMessageBox.warning(self, "Ошибка", "Такого аккаунта не существует")
            return

        self.window = MainWindow(account)
        self.window.show()
        self.close()

    def guest_login(self):
        self.window = MainWindow()
        self.window.show()
        self.close()




app = QApplication([])
window = AuthWindow()
window.show()
app.exec()

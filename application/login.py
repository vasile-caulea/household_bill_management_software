from PyQt6.QtCore import QRunnable, pyqtSlot, QThreadPool, QRect, Qt, QMetaObject
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QMessageBox, QLineEdit, QLabel, QPushButton

from DBConnenction import DBConn
from gu import msgQueue


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)


class LogInDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()

        self.popup = QMessageBox()
        self.popup.setFont(QFont('Arial', pointSize=10))
        self.popup.setWindowTitle('Info')

        self.resize(400, 300)
        self.setWindowTitle("Log in DB")
        self.text_user = QLineEdit(self)
        self.text_user.setGeometry(QRect(90, 100, 231, 31))
        self.text_user.setPlaceholderText("User")

        self.text_password = QLineEdit(self)
        self.text_password.setGeometry(QRect(90, 150, 231, 31))
        self.text_password.setPlaceholderText("Password")
        self.text_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.title_label = QLabel(self)
        self.title_label.setGeometry(QRect(140, 30, 121, 41))
        self.title_label.setFont(QFont('Arial', pointSize=20))
        self.title_label.setText("Log in DB")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.log_button = QPushButton(self)
        self.log_button.setGeometry(QRect(90, 220, 231, 31))
        self.log_button.setText("Log in")
        self.log_button.clicked.connect(self.log_in)

    def log_in(self):
        usr = self.text_user.text()
        passw = self.text_password.text()
        if len(usr) > 0 and len(passw) > 0:
            self.log_button.setText('Connecting to database...')
            self.log_button.setDisabled(True)
            self.text_password.setDisabled(True)
            self.text_user.setDisabled(True)

            worker = Worker(self.do_task, usr, passw)
            self.threadpool.start(worker)
        else:
            self.popup.setText('Invalid fields length')
            self.popup.show()

    def do_task(self, usr, passw):
        try:
            c = DBConn()
            c.connect(usr, passw)

            value = msgQueue.get()
            if type(value) is str:
                self.popup.setText(value)
                self.log_button.setDisabled(False)
                self.log_button.setText('Log in')
                self.text_password.setDisabled(False)
                self.text_user.setDisabled(False)
                QMetaObject.invokeMethod(self.popup, "show")
            else:
                msgQueue.put_nowait(True)
                QMetaObject.invokeMethod(self, "accept")

        except Exception as e:
            print(e)

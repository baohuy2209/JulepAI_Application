from PyQt6.QtWidgets import QApplication, QMainWindow

from backend.ApplicationWindowExt import ApplicationWindowExt

app = QApplication([])
myWindow = ApplicationWindowExt()
MainWindow = QMainWindow()
myWindow.setupUi(MainWindow)
myWindow.show()
app.exec()
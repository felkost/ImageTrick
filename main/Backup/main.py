import sys
import cv2
import numpy as np
# import the interface
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QFileDialog

from Backup.qtmain import *
from PyQt5 import QtCore, QtGui, QtWidgets


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.step = 0
        self.original = []
        self.modified = []
        self.files = []

        self.ui.actionOpen.triggered.connect(lambda: self.openFiles())
        self.ui.lhSlider.valueChanged.connect(lambda: self.value_changed(self.step, self.files))
        self.ui.lsSlider.valueChanged.connect(lambda: self.value_changed(self.step, self.files))
        self.ui.lvSlider.valueChanged.connect(lambda: self.value_changed(self.step, self.files))

        self.ui.uhSlider.valueChanged.connect(lambda: self.value_changed(self.step, self.files))
        self.ui.usSlider.valueChanged.connect(lambda: self.value_changed(self.step, self.files))
        self.ui.uvSlider.valueChanged.connect(lambda: self.value_changed(self.step, self.files))

    def value_changed(self, step, array):
        frame = cv2.imread(array[step])
        self.resize_image(frame)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        l_b = np.array([self.ui.lhSlider.value(), self.ui.lsSlider.value(), self.ui.lvSlider.value()])
        u_b = np.array([self.ui.uhSlider.value(), self.ui.usSlider.value(), self.ui.uvSlider.value()])

        mask = cv2.inRange(hsv, l_b, u_b)

        res = cv2.bitwise_and(frame, frame, mask=mask)
        cv2.imwrite('res.jpg', res)
        image = QImage()
        try:
            if not image.load('res.jpg'):
                self.ui.colorimage.setText(
                    "Selected file is not an image, please select another.")
                return

            self.ui.colorimage.setPixmap(QPixmap.fromImage(image))
        except FileNotFoundError:
            print("theres no such file")

    def openFiles(self):
        try:
            index = self.ui.taskManager.currentIndex()
            self.files = []
            self.step = 0
            self.files, _ = QFileDialog.getOpenFileNames(self, None, None, "Images (*.png *.xpm *.jpg *.jpeg)")
            print(self.files)
            file = self.files[self.step]
            image = QImage()
            if not image.load(file):
                self.ui.colorimage.setText(
                    "Selected file is not an image, please select another.")
                return

            self.ui.colorimage.setPixmap(QPixmap.fromImage(image))
        except IndexError:
            print("list index out of range")

    @staticmethod
    def set_image(step, array, image):
        file = array[step]
        fimage = QImage()
        if not fimage.load(file):
            image.setText(
                "Selected file is not an image, please select another.")
            return

        image.setPixmap(QPixmap.fromImage(fimage))

    # display last image
    def left_button(self):
        if self.step > 0:
            try:
                self.step -= 1
                self.set_image(self.step, self.original, self.ui.firstimages)

                self.set_image(self.step, self.modified, self.ui.secondimages)
            except IndexError:
                print("list index out of range")

    # display next image
    def right_button(self):
        if self.step <= self.original.__len__() - 1:
            try:
                self.step += 1
                self.set_image(self.step, self.original, self.ui.firstimages)

                self.set_image(self.step, self.modified, self.ui.secondimages)
            except IndexError:
                print("list index out of range")

    @staticmethod
    def resize_image(image):
        width = 1920
        height = 1440
        dim = (width, height)
        resized = cv2.resize(image, dim, interpolation=cv2.INTER_CUBIC)
        return resized


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())

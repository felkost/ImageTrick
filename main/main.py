import sys
import cv2
import numpy as np
# import the interface
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QDialog, QVBoxLayout, QLabel, QSizePolicy

import FocusStack
from image_diff import *
from colorDetection import *
from qtmain import *
from image_mask import *
from PyQt5 import QtCore, QtGui, QtWidgets


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.step = 0
        self.original5 = []
        self.modified5 = []
        self.task6 = []
        self.task2 = []
        self.Path = '/home/mickle/PycharmProjects/TUI/Input/'

        self.ui.actionOpen.triggered.connect(lambda: self.openFiles(self.ui.taskManager.currentIndex()))
        self.ui.findColors.clicked.connect(lambda: self.colorChanges(self.task6[0], 8))
        self.ui.l_button.clicked.connect(lambda: self.left_button(1))
        self.ui.r_button.clicked.connect(lambda: self.right_button(1))
        self.ui.l_button_2.clicked.connect(lambda: self.left_button(0))
        self.ui.r_button_2.clicked.connect(lambda: self.right_button(0))
        self.ui.load1images.clicked.connect(lambda: self.openFiles(51))
        self.ui.load2images.clicked.connect(lambda: self.openFiles(52))
        self.ui.actionFind_the_difference.triggered.connect(lambda: self.find_difference())
        self.ui.actionFocus_stacking.triggered.connect(lambda: self.do_stacking())

        self.ui.listColor.itemClicked.connect(lambda: self.changeImage())

    # TODO finish task6
    def changeImage(self):
        item = self.ui.listColor.selectedItems()
        currentBrush = item[-1].background()
        rgbColor = currentBrush.color().red(), currentBrush.color().green(), currentBrush.color().blue()
        image_mask(rgbColor, self.files[0])
        image = QImage()
        if not image.load("res.jpg"):
            self.ui.task6Image.setText(
                "Selected file is not an image, please select another.")
            return

        self.ui.task6Image.setPixmap(QPixmap.fromImage(image))

    def colorChanges(self, filename, number_of_colors):
        try:
            if self.ui.listColor.count() != 0:
                self.ui.listColor.clear()

            rgb, colors = get_colors(get_image(filename), number_of_colors, False)
            for i in range(colors.__len__()):
                n = QListWidgetItem('%s' % (i + 1))
                print(colors[i])
                # print(tuple(map(tuple, colors[i].astype(int))))
                n.setBackground(QColor(colors[i]))
                self.ui.listColor.addItem(n)
        except IndexError:
            print("There`s no file to proceed")

    def find_difference(self):
        try:
            for i in range(self.original5.__len__()):
                image_diff(self.original5[i], self.modified5[i], "original%d.png" % i, "modified%d.png" % i)
                self.original5[i] = "/home/mickle/PycharmProjects/TUI/Output6/original%d.png" % i
                self.modified5[i] = "/home/mickle/PycharmProjects/TUI/Output6/modified%d.png" % i

            self.set_image(0, self.original5, self.ui.firstimages)
            self.set_image(0, self.modified5, self.ui.secondimages)
        except FileNotFoundError:
            print("there are no such files")

    def do_stacking(self):
        try:
            # delete old files from Input directory
            for the_file in os.listdir(self.Path):
                file_path = os.path.join(self.Path, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

            # add images that are showed right now and resize them
            ar_length = len(self.task2)
            for f in range(ar_length):
                img = cv2.imread(self.task2[f])
                width = 1920
                height = 1440
                dim = (width, height)
                resized = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(os.path.join(self.Path, '%d.jpg' % f), resized)
                cv2.waitKey(0)

            # focus-stacking starts here
            hello = self.task2
            hello = sorted(os.listdir(self.Path))
            for img in hello:
                if img.split(".")[-1].lower() not in ["jpg", "jpeg", "png"]:
                    hello.remove(img)

            focusimages = []

            for img in hello:
                print("Reading in file {}".format(img))
                focusimages.append(cv2.imread("/home/mickle/PycharmProjects/TUI/Input/{}".format(img)))

            merged = FocusStack.focus_stack(focusimages)
            cv2.imwrite("/home/mickle/PycharmProjects/TUI/merged.png", merged)
            try:
                self.focus_dialog('/home/mickle/PycharmProjects/TUI/merged.png')
            except FileNotFoundError:
                print("There is no file called merged.png")
        except FileNotFoundError:
            print("There are no files in self.files variable")

    # show the result as dialog
    def focus_dialog(self, file):
        dialog = QDialog(self)
        dialog.setWindowTitle("ImageTrick")
        dialog.resize(800, 600)
        vbox = QVBoxLayout()
        label = QLabel()
        label.setScaledContents(True)
        image = QPixmap(file)
        label.setPixmap(image)
        label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        vbox.addWidget(label)
        dialog.setLayout(vbox)
        dialog.show()

    def openFiles(self, indicator):
        print(indicator)
        try:
            # task 2
            if indicator == 1:
                self.task2 = []
                self.step = 0
                self.task2, _ = QFileDialog.getOpenFileNames(self, None, None, "Images (*.png *.xpm *.jpg *.jpeg)")
                print(self.task2)
                self.set_image(self.step, self.task2, self.ui.image_label)
                self.ui.filename_label.setText(self.task2[self.step])
            # task 5
            elif indicator == 51:
                self.step = 0
                self.original5, _ = QFileDialog.getOpenFileNames(self, None, None,
                                                                 "Images (*.png *.xpm *.jpg *.jpeg)")
                print(self.original5)
                self.set_image(self.step, self.original5, self.ui.firstimages)
            # task 5
            elif indicator == 52:
                self.step = 0
                self.modified5, _ = QFileDialog.getOpenFileNames(self, None, None,
                                                                 "Images (*.png *.xpm *.jpg *.jpeg)")
                print(self.modified5)
                self.set_image(self.step, self.modified5, self.ui.secondimages)
            # task 6
            elif indicator == 4:
                self.task6 = []
                self.step = 0
                self.task6, _ = QFileDialog.getOpenFileNames(self, None, None, "Images (*.png *.xpm *.jpg *.jpeg)")
                self.set_image(self.step, self.task6, self.ui.task6Image)
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
    def left_button(self, indicator):
        if self.step > 0:
            try:
                if indicator == 0:
                    self.step -= 1
                    self.set_image(self.step, self.task2, self.ui.image_label)
                    self.ui.filename_label.setText(self.task2[self.step])
                else:
                    self.step -= 1
                    self.set_image(self.step, self.original5, self.ui.firstimages)
                    self.set_image(self.step, self.modified5, self.ui.secondimages)
            except IndexError:
                print("list index out of range")

    # display next image
    def right_button(self, indicator):
        try:
            if indicator == 0:
                if self.step <= self.task2.__len__() - 1:
                    self.step += 1
                    self.set_image(self.step, self.task2, self.ui.image_label)
                    self.ui.filename_label.setText(self.task2[self.step])
            else:
                if self.step <= self.original5.__len__() - 1:
                    self.step += 1
                    self.set_image(self.step, self.original5, self.ui.firstimages)
                    self.set_image(self.step, self.modified5, self.ui.secondimages)
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

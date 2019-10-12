import sys
import time

import cv2
import numpy as np
# import the interface
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QDialog, QVBoxLayout, QLabel, QSizePolicy

from MapWindow import *
import FocusStack
import glob
from image_diff import *
from colorDetection import *
from qtmain import *
from image_mask import *
from PyQt5 import QtCore, QtGui, QtWidgets
import subprocess


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.step = 0
        self.i = 0
        self.original5 = []
        self.modified5 = []
        self.task6 = []
        self.task2 = []
        self.cwd = os.getcwd()
        print(self.cwd)

        # BODYA
        self.image_window = MapWindow()
        self.ui.pushButton.clicked.connect(self.setAllOptions)
        self.ui.pushButton.clicked.connect(self.image_window.createWindow)
        self.ui.pushButton_2.clicked.connect(self.selectFile)

        self.ui.actionOpen.triggered.connect(lambda: self.openFiles(self.ui.taskManager.currentIndex()))
        self.ui.findColors.clicked.connect(lambda: self.colorChanges())
        self.ui.l_button.clicked.connect(lambda: self.left_button(1))
        self.ui.r_button.clicked.connect(lambda: self.right_button(1))
        self.ui.l_button_2.clicked.connect(lambda: self.left_button(0))
        self.ui.r_button_2.clicked.connect(lambda: self.right_button(0))
        self.ui.load1images.clicked.connect(lambda: self.openFiles(51))
        self.ui.load2images.clicked.connect(lambda: self.openFiles(52))
        self.ui.actionFind_the_difference.triggered.connect(lambda: self.find_difference())
        self.ui.actionFocus_stacking.triggered.connect(lambda: self.do_stacking())
        self.ui.actionMake_the_video.triggered.connect(lambda: self.make_video())

        self.ui.listColor.itemClicked.connect(lambda: self.changeImage())

    def make_video(self):
        try:
            img_arr = []
            # write images in Input directory
            for f in range(self.task2.__len__()):
                img = cv2.imread(self.task2[f])
                width = 1920
                height = 1440
                dim = (width, height)
                resized = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(os.path.join(self.cwd + "/Input4/", '%d.jpg' % f), resized)
                cv2.waitKey(0)
            # fetch all images and make avi file
            for f in range(self.task2.__len__()):
                img = cv2.imread(self.task2[f])
                height, width, layers = img.shape
                size = (width, height)
                img_arr.append(img)
            out = cv2.VideoWriter(self.cwd + "/Output4/project.avi", cv2.VideoWriter_fourcc(*'DIVX'), 1, size)
            for i in range(len(img_arr)):
                out.write(img_arr[i])
            out.release()
        except Exception as e:
            self.error_dialog(str(e))

    def changeImage(self):
        try:
            item = self.ui.listColor.selectedItems()
            currentBrush = item[-1].background()
            rgbColor = currentBrush.color().red(), currentBrush.color().green(), currentBrush.color().blue()
            image_mask(rgbColor, self.task6[0])
            self.focus_dialog(self.cwd + "/Output6/res.jpg")

            # hsvColor = cv2.cvtColor(np.array(rgbColor), cv2.COLOR_RGB2HSV)
            # print(hsvColor)
            # print(hsvColor)
            # measure = hsvColor[1] / 100
            # self.ui.saturationMeasure.setText(measure)
        except Exception as e:
            self.error_dialog(str(e))

    def colorChanges(self):
        number_of_colors = int(self.showDialog())
        try:
            if self.ui.listColor.count() != 0:
                self.ui.listColor.clear()

            rgb, colors = get_colors(get_image(self.task6[0]), number_of_colors, False)
            for i in range(colors.__len__()):
                n = QListWidgetItem('%s' % (i + 1))
                print(colors[i])
                # print(tuple(map(tuple, colors[i].astype(int))))
                n.setBackground(QColor(colors[i]))
                self.ui.listColor.addItem(n)
        except Exception as e:
            self.error_dialog(str(e))

    def showDialog(self):
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter integer:')
        if ok:
            return text

    def find_difference(self):
        try:
            for i in range(self.original5.__len__()):
                image_diff(self.original5[i], self.modified5[i], "original%d.png" % i, "modified%d.png" % i)
                self.original5[i] = self.cwd + "/Output5/original%d.png" % i
                self.modified5[i] = self.cwd + "/Output5/modified%d.png" % i

            self.set_image(0, self.original5, self.ui.firstimages)
            self.set_image(0, self.modified5, self.ui.secondimages)
        except Exception as e:
            self.error_dialog(str(e))

    def do_stacking(self):
        try:
            # delete old files from InputFocus directory
            for the_file in os.listdir(self.cwd + "/InputFocus/"):
                file_path = os.path.join(self.cwd + "/InputFocus/", the_file)
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
                cv2.imwrite(os.path.join(self.cwd + "/InputFocus/", '%d.jpg' % f), resized)
                cv2.waitKey(0)

            # focus-stacking starts here
            hello = self.task2
            hello = sorted(os.listdir(self.cwd + "/InputFocus/"))
            for img in hello:
                if img.split(".")[-1].lower() not in ["jpg", "jpeg", "png"]:
                    hello.remove(img)

            focusimages = []

            for img in hello:
                print("Reading in file {}".format(img))
                focusimages.append(cv2.imread(self.cwd + "/InputFocus/{}".format(img)))

            merged = FocusStack.focus_stack(focusimages)
            cv2.imwrite(self.cwd + "/OutputFocus/merged%d.png" % self.i, merged)
            try:
                self.focus_dialog(self.cwd + '/OutputFocus/merged%d.png' % self.i)
            except Exception as e:
                self.error_dialog(str(e))
            self.i = self.i + 1
        except Exception as e:
            self.error_dialog(str(e))

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
            elif indicator == 3:
                self.task6 = []
                self.step = 0
                self.task6, _ = QFileDialog.getOpenFileNames(self, None, None, "Images (*.png *.xpm *.jpg *.jpeg)")
                self.set_image(self.step, self.task6, self.ui.task6Image)
        except Exception as e:
            self.error_dialog(str(e))

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

    def error_dialog(self, error):
        dialog = QtWidgets.QErrorMessage(self)
        dialog.showMessage(error)

    # BODYA
    def selectFile(self):
        try:
            self.image_window.map = ''.join(QFileDialog.getOpenFileName()[0])
        except Exception as e:
            self.error_dialog(str(e))

    def setAllOptions(self):
        try:
            self.image_window.focus = float(self.ui.lineEdit_2.text())
            self.image_window.parties_h = self.image_window.parties_h / int(self.ui.lineEdit_8.text())
            self.image_window.parties_w = self.image_window.parties_w / int(self.ui.lineEdit_9.text())
            self.image_window.height_cam = float(self.ui.lineEdit_3.text())
            self.image_window.weight_cam = float(self.ui.lineEdit_6.text())
        except Exception as e:
            self.error_dialog(str(e))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())

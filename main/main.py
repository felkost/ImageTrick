import sys
import time
import random

import cv2
import ffmpeg
import numpy as np
# import the interface
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QDialog, QVBoxLayout, QLabel, QSizePolicy

from MapWindow import *
import FocusStack
import glob
from colorDetection import *
from qtmain import *
from image_mask import *
from PyQt5 import QtCore, QtGui, QtWidgets
import subprocess


class LoadingDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(LoadingDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("ImageTrick")
        self.resize(200, 100)
        self.layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setText("loading...")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.step = 0
        self.i = 0
        self.j = 0
        self.k = 0
        self.original5 = []
        self.modified5 = []
        self.task6 = []
        self.task2 = []
        self.cwd = os.getcwd()

        # BODYA
        self.image_window = MapWindow()
        self.start_acces = [True] * 10
        self.ui.pushButton.clicked.connect(self.setAllOptions)
        self.ui.pushButton_2.clicked.connect(self.selectFile)

        self.ui.actionOptical_Flow.triggered.connect(lambda: self.optical_flow())
        self.ui.actionOpen.triggered.connect(lambda: self.openFiles(self.ui.taskManager.currentIndex()))
        self.ui.findColors.clicked.connect(lambda: self.colorChanges())
        self.ui.l_button.clicked.connect(lambda: self.left_button(1))
        self.ui.r_button.clicked.connect(lambda: self.right_button(1))
        self.ui.l_button_2.clicked.connect(lambda: self.left_button(0))
        self.ui.r_button_2.clicked.connect(lambda: self.right_button(0))
        self.ui.actionFocus_stacking.triggered.connect(lambda: self.do_stacking())
        self.ui.actionMake_the_video.triggered.connect(lambda: self.make_video())

        self.ui.listColor.itemClicked.connect(lambda: self.changeImage())

    def make_video(self):
        try:
            # delete old files from InputFocus directory
            for the_file in os.listdir(self.cwd + "/InputVideo/"):
                file_path = os.path.join(self.cwd + "/InputVideo/", the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    self.error_dialog(str(e))
            # write images in Input directory
            for f in range(self.task2.__len__()):
                img = cv2.imread(self.task2[f])
                width = 1920
                height = 1440
                dim = (width, height)
                resized = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(os.path.join(self.cwd + "/InputVideo/", '%d.jpg' % f), resized)
                cv2.waitKey(0)
            # fetch all images and make mp4 file
            (
                ffmpeg
                .input(self.cwd + '/InputVideo/*.jpg', pattern_type='glob', framerate=int(self.showDialog("FPS: ")))
                .output(self.cwd + '/OutputVideo/movie%d.mp4' % self.k)
                .overwrite_output()
                .run()
            )
            self.show_video(self.cwd + '/OutputVideo/movie%d.mp4' % self.k)
            self.k = self.k + 1
        except Exception as e:
            self.error_dialog(str(e))

    def show_video(self, file):
        cap = cv2.VideoCapture(file)

        # Check if camera opened successfully
        if not cap.isOpened():
            self.error_dialog("Error opening video stream or file")

        # Read until video is completed
        while cap.isOpened():
            # Capture frame-by-frame
            ret, frame = cap.read()
            if ret:

                # Display the resulting frame
                cv2.imshow('Frame', frame)
                cv2.waitKey(200)
                # Press Q on keyboard to  exit
                if cv2.waitKey(210) & 0xFF == ord('q'):
                    break

            # Break the loop
            else:
                break

        # When everything done, release the video capture object
        cap.release()

        # Closes all the frames
        cv2.destroyAllWindows()

    def optical_flow(self):
        try:
            # delete old files from InputFocus directory
            for the_file in os.listdir(self.cwd + "/InputVideo/"):
                file_path = os.path.join(self.cwd + "/InputVideo/", the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    self.error_dialog(str(e))
            # write images in Input directory
            for f in range(self.task2.__len__()):
                img = cv2.imread(self.task2[f])
                width = 1920
                height = 1440
                dim = (width, height)
                resized = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(os.path.join(self.cwd + "/InputVideo/", '%d.jpg' % f), resized)
                cv2.waitKey(0)
            # fetch all images and make mp4 file
            (
                ffmpeg
                .input(self.cwd + '/InputVideo/*.jpg', pattern_type='glob', framerate=int(self.showDialog("FPS: ")))
                .output(self.cwd + '/OutputFLow/movie%d.mp4' % self.j)
                .overwrite_output()
                .run()
            )
            cap = cv2.VideoCapture(self.cwd + '/OutputFLow/movie%d.mp4' % self.j)
            self.j = self.j + 1

            ret, first_frame = cap.read()
            prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
            # Creates an image filled with zero intensities with the same dimensions as the frame
            mask = np.zeros_like(first_frame)
            # Sets image saturation to maximum
            mask[..., 1] = 255
            i = 0
            while cap.isOpened():
                ret, frame = cap.read()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                mask[..., 0] = angle * 180 / np.pi / 2
                mask[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
                rgb = cv2.cvtColor(mask, cv2.COLOR_HSV2BGR)
                cv2.imshow("dense optical flow", rgb)
                cv2.imwrite(os.getcwd() + '/OutputFLow/flow' + str(i) + '.jpg', rgb)
                self.modified5.append(os.getcwd() + '/OutputFLow/flow' + str(i) + '.jpg')
                i = i + 1
                prev_gray = gray
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            pass

        self.original5 = self.task2
        self.step = 0
        self.set_image(self.step, self.original5, self.ui.firstimages)
        self.set_image(self.step, self.modified5, self.ui.secondimages)

    def changeImage(self):
        try:
            item = self.ui.listColor.selectedItems()
            currentBrush = item[-1].background()
            rgbColor = currentBrush.color().red(), currentBrush.color().green(), currentBrush.color().blue()
            image_mask(rgbColor, self.task6[0])
            self.focus_dialog(self.cwd + "/OutputColorDetection/res.jpg")

            # color = np.uint8([[[rgbColor]]])
            # hsvColor = cv2.cvtColor(color, cv2.COLOR_RGB2HSV)
            # measure = hsvColor[1] / 100
            #measure = random.uniform(0.0, 1.0)
            #self.ui.saturationMeasure.setText(str(measure))
        except Exception as e:
            self.error_dialog(str(e))

    def colorChanges(self):
        dlg = LoadingDialog(self)
        dlg.show()
        number_of_colors = int(self.showDialog("Кількість кольорів: "))
        try:
            if self.ui.listColor.count() != 0:
                self.ui.listColor.clear()

            rgb, colors = get_colors(get_image(self.task6[0]), number_of_colors, False)
            for i in range(colors.__len__()):
                n = QListWidgetItem('%s' % (i + 1))
                n.setBackground(QColor(colors[i]))
                self.ui.listColor.addItem(n)
            dlg.close()
        except Exception as e:
            self.error_dialog(str(e))

    def showDialog(self, text):
        text, ok = QInputDialog.getText(self, 'Input Dialog', text)
        if ok:
            return text

    def do_stacking(self):
        try:
            dlg = LoadingDialog(self)
            dlg.show()
            # delete old files from InputFocus directory
            for the_file in os.listdir(self.cwd + "/InputFocus/"):
                file_path = os.path.join(self.cwd + "/InputFocus/", the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    self.error_dialog(str(e))

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
                focusimages.append(cv2.imread(self.cwd + "/InputFocus/{}".format(img)))

            merged = FocusStack.focus_stack(focusimages)
            cv2.imwrite(self.cwd + "/OutputFocus/merged%d.png" % self.i, merged)
            dlg.close()
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
        try:
            # task 2
            if indicator == 1:
                self.task2 = []
                self.step = 0
                self.task2, _ = QFileDialog.getOpenFileNames(self, None, "/home/mickle/Project", "Images (*.png *.xpm "
                                                                                                 "*.jpg *.jpeg)")
                self.set_image(self.step, self.task2, self.ui.image_label)
                self.ui.filename_label.setText(self.task2[self.step])
            # task 5
            elif indicator == 51:
                self.step = 0
                self.original5, _ = QFileDialog.getOpenFileNames(self, None, "/home/mickle/Project",
                                                                 "Images (*.png *.xpm *.jpg *.jpeg)")
                self.set_image(self.step, self.original5, self.ui.firstimages)
            # task 5
            elif indicator == 52:
                self.step = 0
                self.modified5, _ = QFileDialog.getOpenFileNames(self, None, "/home/mickle/Project",
                                                                 "Images (*.png *.xpm *.jpg *.jpeg)")
                self.set_image(self.step, self.modified5, self.ui.secondimages)
            # task 6
            elif indicator == 3:
                self.task6 = []
                self.step = 0
                self.task6, _ = QFileDialog.getOpenFileNames(self, None, "/home/mickle/Project", "Images (*.png *.xpm "
                                                                                                 "*.jpg *.jpeg)")
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
                self.error_dialog("list index out of range")

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
            self.error_dialog("list index out of range")

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
            self.image_window.map = ''.join(QFileDialog.getOpenFileName(self, None, "/home/mickle/Project")[0])
        except Exception as e:
            self.error_dialog(str(e))

    def setAllOptions(self):
        try:
            self.image_window.acces = True
            if self.image_window.map == '':
                self.start_acces[0] = False
            else:
                self.start_acces[0] = True

            if float(self.ui.lineEdit.text()) < 0:
                self.start_acces[1] = False
            else:
                self.image_window.height_point.max_height = float(self.ui.lineEdit.text())
                self.start_acces[1] = True

            if float(self.ui.lineEdit_2.text()) < 0:
                self.start_acces[2] = False
            else:
                self.image_window.focus = float(self.ui.lineEdit_2.text())
                self.start_acces[2] = True

            if int(self.ui.lineEdit_8.text()) < 0:
                self.start_acces[3] = False
            else:
                self.image_window.parties_h = self.image_window.parties_h / int(self.ui.lineEdit_8.text())
                self.start_acces[3] = True

            if int(self.ui.lineEdit_9.text()) < 0:
                self.start_acces[4] = False
            else:
                self.image_window.parties_w = self.image_window.parties_w / int(self.ui.lineEdit_9.text())
                self.start_acces[4] = True

            if float(self.ui.lineEdit_3.text()) < 0:
                self.start_acces[5] = False
            else:
                self.image_window.height_cam = float(self.ui.lineEdit_3.text())
                self.start_acces[5] = True

            if float(self.ui.lineEdit_6.text()) < 0:
                self.start_acces[6] = False
            else:
                self.image_window.weight_cam = float(self.ui.lineEdit_6.text())
                self.start_acces[6] = True

            if float(self.ui.lineEdit_7.text()) < 0 or float(self.ui.lineEdit_7.text()) > 100:
                self.start_acces[7] = False
            else:
                self.image_window.percent_start = float(self.ui.lineEdit_7.text())
                self.start_acces[7] = True

            if float(self.ui.lineEdit_5.text()) < 0 or float(self.ui.lineEdit_5.text()) > 100:
                self.start_acces[8] = False
            else:
                self.image_window.percent_per_hundred = float(self.ui.lineEdit_5.text())
                self.start_acces[8] = True

            if float(self.ui.lineEdit_4.text()) < 0 or float(self.ui.lineEdit_4.text()) > 100:
                self.start_acces[9] = False
            else:
                self.image_window.percent_per_photo = float(self.ui.lineEdit_4.text())
                self.start_acces[9] = True

            for i in self.start_acces:
                if not i:
                    self.image_window.acces = False

            self.image_window.createWindow()
        except Exception as e:
            self.error_dialog(str(e))

    def callError(self, message):
        QMessageBox.about(self, "Помилка", message)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())

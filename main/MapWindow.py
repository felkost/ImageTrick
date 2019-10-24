# coding=utf-8
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qtmain import *
from main import *
import math
import numpy as np


class Height(QDialog):
    def __init__(self, parent=None):
        super(Height, self).__init__(parent)
        self.enterHeight = QPushButton("Підтвердити")
        self.enterHeight.setGeometry(QtCore.QRect(240, 800, 250, 100))
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setGeometry(QtCore.QRect(20, 60, 150, 41))
        self.lineEdit.setObjectName("lineEdit")
        self.height = 0.00
        self.max_height = 0.00
        layout = QHBoxLayout()
        layout.addWidget(self.enterHeight)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)
        self.enterHeight.clicked.connect(self.takeHeight)

    def takeHeight(self):
        if self.lineEdit.text():
            self.height = float(self.lineEdit.text())
        else:
            self.height = 0.00
        if self.height > self.max_height:
            self.callError("Висота більша за максимальну")
        elif self.height < 0:
            self.callError("Дані введені не коректно")
        else:
            self.close()

    def createWindow(self):
        self.setGeometry(250, 100, 250, 100)
        self.setWindowTitle("Висота")
        self.show()

    def callError(self, message):
        QMessageBox.about(self, "Помилка", message)


class MapWindow(QDialog):
    def __init__(self, parent=None):
        super(MapWindow, self).__init__(parent)
        self.end_points = QPushButton("Закінчити редагування точок", self)
        self.end_points.clicked.connect(self.finishPoints)
        self.height_point = Height()
        self.points = []
        self.ways = [0]
        self.angels = []
        self.rects = []
        self.heights = []
        self.count = -1
        self.focus = 0.00
        self.height_cam = 0.00
        self.weight_cam = 0.00
        self.map = ''
        self.parties_h = 800
        self.parties_w = 1250
        self.height_poly = []
        self.weight_poly = []
        self.bool_end = False
        self.percent_bool_end = False
        self.percent_start = 0
        self.percent_per_hundred = 0
        self.percent_per_photo = 0
        self.acces = True
        self.percent_point = []
        self.photo_way = []
        self.percent = QLabel(str(self.percent_start), self)

    def createWindow(self):
        if self.acces:
            self.percent_point.append(self.percent_start)
            self.percent.setText("Заряд дрона " + str(self.percent_start) + "%")
            self.percent.move(850, 2)
            self.percent.setFont(QFont('ubuntu', 24))
            self.end_points.move(2, 802)
            self.end_points.resize(500, 30)
            self.setGeometry(250, 250, 1250, 900)
            self.setWindowTitle("Мапа")
            self.show()
        else:
            self.callError("Дані введені не коректно")

    def mousePressEvent(self, event):
        heigts_difference = 0.0
        self.count += 1
        self.height_point.createWindow()
        self.points.append(np.array([event.pos().x(), event.pos().y(), 0]))
        self.focusArea(self.count)
        self.heights.append(self.height_point.height)
        self.weight_poly.append(((self.weight_cam / 1000) * self.heights[self.count] / (self.focus / 1000))
                                * self.parties_h)
        self.height_poly.append(((self.height_cam / 1000) * self.heights[self.count] / (self.focus / 1000))
                                * self.parties_w)
        if self.count > 0:
            self.ways[0] = int(float(np.linalg.norm(self.points[self.count] - self.points[0])
                                     + self.height_poly[self.count]) / self.height_poly[self.count])
            self.ways.append(int(float(np.linalg.norm(self.points[self.count - 1] - self.points[self.count])
                                       + self.height_poly[self.count]) / self.height_poly[self.count]))
            self.percentAfterWay(self.points[self.count - 1], self.points[self.count])

        if self.count == 0:
            self.percent_point[self.count] -= (self.heights[self.count] / 100) * self.percent_per_hundred
        else:
            heigts_difference = self.heights[self.count] - self.heights[self.count - 1]
            if heigts_difference > 0:
                self.percent_point[self.count] -= (heigts_difference / 100) * self.percent_per_hundred
            self.percent_point[self.count] -= self.ways[self.count] * self.percent_per_photo
        self.percent.setText("Заряд дрона " + str(self.percent_point[len(self.percent_point) - 1]) + "%")

    def percentAfterWay(self, point1, point2):
        point_way1 = np.array([point1[0] / self.parties_h, point1[1] / self.parties_w])
        point_way2 = np.array([point2[0] / self.parties_h, point2[1] / self.parties_w])
        way = np.linalg.norm(point_way1 - point_way2)
        self.percent_point.append(self.percent_point[len(self.percent_point) - 1]
                                  - (way / 100) * self.percent_per_hundred)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        pixmap = QtGui.QPixmap()
        pixmap.load(self.map)
        painter.drawPixmap(0, 0, 1250, 800, pixmap)
        painter.setPen(QPen(Qt.red, 5, Qt.SolidLine))
        for i in range(len(self.points)):
            painter.drawEllipse(self.points[i][0], self.points[i][1], 8, 8)
            if len(self.points) > 1:
                line = QtCore.QLine(QtCore.QPoint(self.points[i - 1][0], self.points[i - 1][1]),
                                    QtCore.QPoint(self.points[i][0], self.points[i][1]))
                painter.drawLine(line)
            if i > 0:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(239, 8, 45, 100)))
                for j in range(self.ways[i]):
                    temp_point = self.findStepLine(self.points[i - 1], self.points[i], j, self.height_poly[i])
                    painter.drawPolygon(
                        self.createPolygon(4, math.sqrt(self.height_poly[i] ** 2 + self.height_poly[i] ** 2) / 2,
                                           # радіус рівний половині діагоналі
                                           self.angels[i], temp_point[0], temp_point[1],
                                           self.weight_poly[i] - self.height_poly[i]))
        if self.bool_end:
            a = self.points[len(self.points) - 2]
            b = self.points[len(self.points) - 1]
            c = self.points[0]
            vector_ba = b - a
            vector_bc = b - c
            mod_ba = np.linalg.norm(a - b)
            mod_bc = np.linalg.norm(c - b)
            scalar_ba_bc = np.dot(vector_ba, vector_bc)
            cos_b = scalar_ba_bc / (mod_ba * mod_bc)
            end_angel = -math.degrees(math.acos(cos_b)) + self.angels[len(self.angels) - 1]
            painter.setBrush(QtGui.QBrush(QtGui.QColor(239, 8, 45, 100)))
            for j in range(self.ways[0]):
                temp_point = self.findStepLine(self.points[len(self.points) - 1], self.points[0], j,
                                               self.height_poly[len(self.height_poly) - 1])
                painter.drawPolygon(
                    self.createPolygon(4, math.sqrt(self.height_poly[len(self.height_poly) - 1] ** 2
                                                    + self.height_poly[len(self.height_poly) - 1] ** 2) / 2,
                                       end_angel, temp_point[0], temp_point[1],
                                       self.weight_poly[len(self.weight_poly) - 1] -
                                       self.height_poly[len(self.height_poly) - 1]))
            if self.percent_bool_end:
                self.percentAfterWay(self.points[len(self.points) - 1], self.points[0])
                self.percent_point[self.count] -= self.ways[0] * self.percent_per_photo
                self.percent.setText("Заряд дрона " + str(int(self.percent_point[len(self.percent_point) - 1])) + "%")
            self.percent_bool_end = False
        painter.end()
        self.update()

    def focusArea(self, i):
        if len(self.points) > 2:
            a = self.points[i - 2]
            b = self.points[i - 1]
            c = self.points[i]
            vector_ba = b - a
            vector_bc = b - c
            mod_ba = np.linalg.norm(a - b)
            mod_bc = np.linalg.norm(c - b)
            scalar_ba_bc = np.dot(vector_ba, vector_bc)
            cos_b = scalar_ba_bc / (mod_ba * mod_bc)
            self.angels.append(-math.degrees(math.acos(cos_b)) + self.angels[len(self.angels) - 1])

        elif i == 0:
            self.angels.append(0)
        elif 3 > len(self.points) > 0:
            b = self.points[i - 1]
            c = self.points[i]
            a = np.array([c[0], b[1], 0])
            vector_ba = b - a
            vector_bc = b - c
            mod_ba = np.linalg.norm(a - b)
            mod_bc = np.linalg.norm(c - b)
            scalar_ba_bc = np.dot(vector_ba, vector_bc)
            cos_b = scalar_ba_bc / (mod_ba * mod_bc)
            self.angels.append(-math.degrees(math.acos(cos_b)) + self.angels[len(self.angels) - 1])

    def callError(self, message):
        QMessageBox.about(self, "Помилка", message)

    def finishPoints(self):
        self.bool_end = True
        self.percent_bool_end = True

    @staticmethod
    def findStepLine(point1, point2, count, step):  # points[i - 1], points[i]
        len = np.linalg.norm(point1 - point2)
        point3 = point1 + (point2 - point1) * ((count * step) / len)
        return point3

    @staticmethod
    def createPolygon(n, r, s, x_coord, y_coord, weight):
        polygon = QtGui.QPolygonF()
        point = []
        w = 360 / n

        t1 = w * 0 + s + 45
        x1 = r * math.cos(math.radians(t1))
        y1 = r * math.sin(math.radians(t1))
        point.append(np.array([x1, y1, 0]))

        t2 = w * 1 + s + 45
        x2 = r * math.cos(math.radians(t2))
        y2 = r * math.sin(math.radians(t2))
        point.append(np.array([x2, y2, 0]))

        t3 = w * 2 + s + 45
        x3 = r * math.cos(math.radians(t3))
        y3 = r * math.sin(math.radians(t3))
        point.append(np.array([x3, y3, 0]))

        t4 = w * 3 + s + 45
        x4 = r * math.cos(math.radians(t4))
        y4 = r * math.sin(math.radians(t4))
        point.append(np.array([x4, y4, 0]))

        len1 = np.linalg.norm(point[3] - point[0])
        temp_point1 = point[3] + (point[0] - point[3]) * ((len1 + weight) / len1)

        len2 = np.linalg.norm(point[2] - point[1])
        temp_point2 = point[2] + (point[1] - point[2]) * ((len2 + weight) / len2)

        len3 = np.linalg.norm(point[1] - point[2])
        temp_point3 = point[1] + (point[2] - point[1]) * ((len3 + weight) / len3)

        len4 = np.linalg.norm(point[0] - point[3])
        temp_point4 = point[0] + (point[3] - point[0]) * ((len4 + weight) / len4)

        polygon.append(QtCore.QPointF(x_coord + temp_point1[0], y_coord + temp_point1[1]))
        polygon.append(QtCore.QPointF(x_coord + temp_point2[0], y_coord + temp_point2[1]))
        polygon.append(QtCore.QPointF(x_coord + temp_point3[0], y_coord + temp_point3[1]))
        polygon.append(QtCore.QPointF(x_coord + temp_point4[0], y_coord + temp_point4[1]))
        return polygon

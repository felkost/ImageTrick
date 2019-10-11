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
        self.enterHeight.setGeometry(QtCore.QRect(240, 80, 250, 100))
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setGeometry(QtCore.QRect(20, 60, 150, 41))
        self.lineEdit.setObjectName("lineEdit")
        self.height = 0
        layout = QHBoxLayout()
        layout.addWidget(self.enterHeight)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)
        self.enterHeight.clicked.connect(self.takeHeight)

    def takeHeight(self):
        if self.lineEdit.text():
            self.height = float(self.lineEdit.text())
        else:
            self.height = 0
        self.close()

    def createWindow(self):
        self.setGeometry(250, 100, 250, 100)
        self.setWindowTitle("Висота")
        self.show()


class MapWindow(QDialog):
    def __init__(self, parent=None):
        super(MapWindow, self).__init__(parent)
        self.points = []
        self.ways = [0]
        self.angels = []
        self.rects = []
        self.heights = []
        self.count = -1
        self.focus = 0.00
        self.height_cam = 0.00
        self.weight_cam = 0.00
        self.height_point = Height()
        self.map = ''
        self.parties_h = 800
        self.parties_w = 1250
        self.height_poly = []
        self.weight_poly = []

    def createWindow(self):
        self.setGeometry(250, 250, 1250, 800)
        self.setWindowTitle("Мапа")
        self.show()

    def mousePressEvent(self, event):
        self.count += 1
        self.height_point.createWindow()
        self.points.append(np.array([event.pos().x(), event.pos().y(), 0]))
        self.rects.append(self.focusArea(self.count))
        if self.count > 0:
            self.heights.append(self.height_point.height)
        else:
            self.heights.append(0)
        self.weight_poly.append(((self.weight_cam / 1000) * self.heights[self.count] / (self.focus / 1000))
                                * self.parties_h)
        self.height_poly.append(((self.height_cam / 1000) * self.heights[self.count] / (self.focus / 1000))
                                * self.parties_w)
        if self.count > 0:
            self.ways[0] = int((np.linalg.norm(self.points[self.count] - self.points[0])
                                + self.height_poly[self.count]) / self.height_poly[self.count])
            self.ways.append(int((np.linalg.norm(self.points[self.count - 1] - self.points[self.count])
                                  + self.height_poly[self.count]) / self.height_poly[self.count]))

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        pixmap = QtGui.QPixmap()
        pixmap.load(self.map)
        painter.drawPixmap(0, 0, 1250, 800, pixmap)
        painter.setPen(QPen(Qt.gray, 5, Qt.SolidLine))
        for i in range(len(self.points)):
            painter.drawEllipse(self.points[i][0], self.points[i][1], 8, 8)
            if len(self.points) > 1:
                line = QtCore.QLine(QtCore.QPoint(self.points[i - 1][0], self.points[i - 1][1]),
                                    QtCore.QPoint(self.points[i][0], self.points[i][1]))
                painter.drawLine(line)
            if i > 0:
                painter.setBrush(QtGui.QBrush(QtGui.QColor(55, 60, 61, 100)))
                for j in range(self.ways[i]):
                    temp_point = self.findStepLine(self.points[i - 1], self.points[i], j, self.height_poly[i])
                    painter.drawPolygon(
                        self.createPolygon(4, math.sqrt(self.height_poly[i] ** 2 + self.height_poly[i] ** 2) / 2,
                                           # радіус рівний половині діагоналі
                                           self.angels[i], temp_point[0], temp_point[1],
                                           self.weight_poly[i] - self.height_poly[i]))

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
            # return self.findPolygonPoints(i)
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

    @staticmethod
    def findStepLine(point1, point2, count, step):  # points[i - 1], points[i]
        len = np.linalg.norm(point1 - point2)
        point3 = point1 + (point2 - point1) * ((count * step) / len)
        return point3

    @staticmethod
    def createPolygon(n, r, s, x_coord, y_coord,
                      weight):  # ОБЕРЕЖНО ГОВНОКОД!!!!!!1!!!!!1!!                           (шучу він скрізь)
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

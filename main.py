#-*-coding:utf-8-*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import glob
import re
import os
import numpy as np
import time

rectangle = True
line_width = 1
items = []
objs = []


class Dragger(QMainWindow):
    def __init__(self, width, height, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.title = 'Dragger'
        self.left = 100
        self.top = 100
        self.width = width
        self.height = height
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, 500, 300)

        # FIle Open on menubar
        openAct = QAction('&Open', self)
        openAct.setShortcut('Ctrl+O')
        openAct.setStatusTip('Open Directory')
        openAct.triggered.connect(self.openFile)

        self.menubar = self.menuBar()
        file = self.menubar.addMenu('&File')
        file.addAction(openAct)

        self.readtime()
        self.timer_widget = Timerwidget(self)
        self.setCentralWidget(self.timer_widget)

        self.show()  # Window 화면 출력

    def readtime(self):
        if os.path.isfile('./time.txt'):
            with open('./time.txt', 'r') as f:
                self.time_sec = int(f.read())
        else:
            self.time_sec = 0

    def savetime(self):
        with open('./time.txt', 'w') as f:
            f.write(str(self.timer_widget.sec))

    def closeEvent(self, QCloseEvent):
        ans = QMessageBox.question(self, "종료 확인", "종료하시겠습니까?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ans == QMessageBox.Yes:
            QCloseEvent.accept()
            self.savetime()
            self.savelastfile()
        else:
            QCloseEvent.ignore()

    def savelastfile(self):
        try:
            p = self.GraphicWidget.img_path
            with open('./file.txt', 'w') as f:
                f.write(p)
        except:
            pass

    def openFile(self):
        if os.path.isfile('./file.txt'):
            with open('./file.txt', 'r') as f:
                self.file_dir = f.readlines()
            ans = QMessageBox.question(self, "기록 확인", "기록을 불러오시겠습니까?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if ans == QMessageBox.Yes:
                self.make_table()  # 메인 위젯의 table에 불러온 file의 데이터 쓰기
            else:
                self.file_dir = QFileDialog.getOpenFileName(self, "Get Dir Path",
                                                            filter='JPG (*.jpg)')  # ;;PNG (*.png)')
                self.make_table()  # 메인 위젯의 table에 불러온 file의 데이터 쓰기
        else:
            self.file_dir = QFileDialog.getOpenFileName(self, "Get Dir Path", filter='JPG (*.jpg)')  # ;;PNG (*.png)')
            self.make_table()  # 메인 위젯의 table에 불러온 file의 데이터 쓰기

    def make_table(self):
        ext_list = ['jpg', 'png', 'JPG']
        self.img_file = self.file_dir[0]
        self.img_list = glob.glob('/'.join(self.img_file.split('/')[:-1]) + '/*')
        self.img_list = [i.replace('\\', '/') for i in self.img_list if i.split('.')[-1] in ext_list]
        self.img_idx = self.img_list.index(self.img_file)

        # main widget 클래스 생성
        self.GraphicWidget = Graphics(self)
        self.GraphicWidget.show()
        self.GraphicWidget.set_image()


class Timerwidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        # 타이머 레이아웃
        timer_layout = QBoxLayout(QBoxLayout.TopToBottom)
        timer_subLayout = QBoxLayout(QBoxLayout.LeftToRight)

        # 타이머 위젯
        self.sec = parent.time_sec
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timeout)

        # 타이머 디스플레이 위젯
        self.lcd = QLCDNumber()
        self.lcd.display('')
        self.lcd.setDigitCount(8)

        # 타이머 시작 버튼
        self.btnStart = QPushButton("시작")
        self.btnStart.clicked.connect(self.onStartButtonClicked)

        # 타이머 멈춤 버튼
        self.btnStop = QPushButton("멈춤")
        self.btnStop.clicked.connect(self.onStopButtonClicked)

        # 타이머 리셋 버튼
        self.btnReset = QPushButton('리셋')
        self.btnReset.clicked.connect(self.onResetButtonClicked)

        # 타이머 상태 설정
        self.btnStop.setEnabled(False)

        timer_layout.addWidget(self.lcd)

        # 타이머 시작, 멈춤 버튼 레이아웃 설정
        timer_subLayout.addWidget(self.btnStart)
        timer_subLayout.addWidget(self.btnStop)
        timer_subLayout.addWidget(self.btnReset)
        timer_layout.addLayout(timer_subLayout)

        self.setLayout(timer_layout)

    def onStartButtonClicked(self):
        self.timer.start()
        self.btnStop.setEnabled(True)
        self.btnStart.setEnabled(False)

    def onStopButtonClicked(self):
        self.timer.stop()
        self.btnStop.setEnabled(False)
        self.btnStart.setEnabled(True)

    def onResetButtonClicked(self):
        self.sec = 0
        currentTime = time.strftime('%H:%M:%S', time.gmtime(self.sec))
        self.lcd.display(currentTime)

    def timeout(self):
        sender = self.sender()
        self.sec += 1
        currentTime = time.strftime('%H:%M:%S', time.gmtime(self.sec))
        if id(sender) == id(self.timer):
            self.lcd.display(currentTime)


class Graphics(QMainWindow):
    def __init__(self, parent=None):
        super(Graphics, self).__init__(parent)

        self.window_w, self.window_h = parent.width - 50, parent.height - 50
        self.top, self.left = parent.top + 20, parent.left + 20
        self.setGeometry(self.top, self.left, self.window_w, self.window_h)
        self.init_file = parent.img_file

        # 파라미터
        self.img_path = parent.img_file
        self.img_idx = parent.img_idx
        self.img_list = parent.img_list

        self.scaleFactor = 1.0

        self._current_rect_item = None

        self._start = QPointF()
        self._current_item = None

        self.c_item_coord = 0

        # 드래그 공간

        scroll = QScrollArea(self)
        scroll.setWidget(self._initGraphics())
        self.setCentralWidget(scroll)
        self.createActions()
        self.createMenus()
        self._start = QPointF()

    def _initGraphics(self):
        self.graphicsView = QGraphicsView(self)
        self.graphicsView.setGeometry(40,30,0,0)
        self.scene = GraphicsScene(self)
        self.pixmap = QGraphicsPixmapItem()
        self.pixmap.setFlags(QGraphicsItem.ItemIsFocusable)
        self.scene.addItem(self.pixmap)
        self.graphicsView.setScene(self.scene)
        return self.graphicsView


    def createActions(self):
        self.zoomInAct = QAction("Zoom &In (25%)", self, shortcut="Ctrl+Z", enabled=True, triggered=self.zoomIn)
        self.zoomOutAct = QAction("Zoom &Out (25%)", self, shortcut="Ctrl+X", enabled=True, triggered=self.zoomOut)
        self.normalSizeAct = QAction("&Normal Size", self, shortcut="Ctrl+A", enabled=True, triggered=self.normalSize)

        self.linewidthAct = QAction("Change Line &Width", self, shortcut='Q', triggered=self.changeline)
        self.rectangleAct = QAction("Change &Shape", self, shortcut='W', triggered=self.changerect)
        self.removeAct = QAction("Remove &Box", self, shortcut='R', triggered=self.removeline)
        self.nextAct = QAction("Next &Image", self, shortcut='Right', triggered=self.nextimage)
        self.prevAct = QAction("Previous &Image", self, shortcut='Left', triggered=self.previmage)
        self.copyitem = QAction('Copy &Box', self, shortcut='Ctrl+C', triggered=self.copy)
        self.pasteitem = QAction('Paste &item', self, shortcut='Ctrl+V', triggered=self.paste)
        self.save = QAction("Save", self, shortcut='Ctrl+S', triggered=self.savetxt)
        self.delete = QAction("Delete &Image", self, shortcut='Ctrl+I', triggered=self.delete_img)

    def createMenus(self):
        menubar = self.menuBar()
        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)

        self.toolMenu = QMenu("&Tools", self)
        self.toolMenu.addAction(self.linewidthAct)
        self.toolMenu.addAction(self.rectangleAct)
        self.toolMenu.addAction(self.removeAct)
        self.toolMenu.addAction(self.nextAct)
        self.toolMenu.addAction(self.prevAct)
        self.toolMenu.addAction(self.copyitem)
        self.toolMenu.addAction(self.pasteitem)
        self.toolMenu.addAction(self.save)
        self.toolMenu.addAction(self.delete)

        menubar.addMenu(self.viewMenu)
        menubar.addMenu(self.toolMenu)
        # menubar.setVisible(False)


    def set_image(self):
        global objs
        self.org_pix = QPixmap(self.img_path)
        self.setWindowTitle(self.img_path)

        # 화면 사이즈 맞춤
        p_w, p_h = self.org_pix.width(), self.org_pix.height()
        pix_wh_ratio = p_w / p_h
        win_wh_ratio = self.window_w / self.window_h

        if pix_wh_ratio > win_wh_ratio:
            self.g_w = self.window_w
            self.g_h = self.g_w / pix_wh_ratio
        elif pix_wh_ratio < win_wh_ratio:
            self.g_h = self.window_h
            self.g_w = self.g_h * pix_wh_ratio
        elif pix_wh_ratio == win_wh_ratio:
            self.g_w, self.g_h = self.window_w, self.window_h
        self.org_pix = self.org_pix.scaled(self.g_w, self.g_h)
        self.graphicsView.resize(self.g_w+2, self.g_h+2)
        self.pixmap.setPixmap(self.org_pix)

        if os.path.isfile(re.sub(r'.jpg|.JPG|.png', '.txt', self.img_path)):
            with open(re.sub(r'.jpg|.JPG|.png', '.txt', self.img_path)) as f:
                objs = f.readlines()
                objs = [list(map(float, i.split())) for i in objs]
        else:
            objs = []

        self.draw_boxes()

    def draw_boxes(self):
        global objs, items, line_width, rectangle

        for i in items:
            self.scene.removeItem(i)
        items = []
        for i in objs:
            color = list(np.random.random(size=3) * 256)  # (255, 255, 0)
            i = self.yolo_to_x_y(*i[1:], self.g_w, self.g_h)

            if rectangle:
                rect_item = QGraphicsRectItem(QRectF(*i))
                rect_item.setPen(QPen(QColor(*color), line_width, Qt.SolidLine))
                rect_item.setFlags(QGraphicsItem.ItemIsSelectable
                                   | QGraphicsItem.ItemIsMovable
                                   | QGraphicsItem.ItemSendsGeometryChanges)
                self.scene.addItem(rect_item)
                items.append(rect_item)
            else:
                circle_item = QGraphicsEllipseItem(*i, i[2])
                circle_item.setPen(QPen(QColor(*color), line_width, Qt.SolidLine))
                self.scene.addItem(circle_item)
                items.append(circle_item)

    def yolo_to_x_y(self, x_center, y_center, x_width, y_height, width, height):
        global rectangle
        x_center *= width
        y_center *= height
        x_width *= width
        y_height *= height
        if rectangle:
            return int(x_center - x_width/2.0), int(y_center - y_height/2.0), int(x_width), int(y_height)
        else:
            radius = min(x_width, y_height)*0.6
            return int(x_center - radius/2), int(y_center -radius/2), int(radius)

    def changeline(self):
        global line_width
        line_width += 1
        if line_width == 4:
            line_width = 1
        self.draw_boxes()

    def changerect(self):
        global rectangle
        rectangle = not rectangle
        self.draw_boxes()

    def removeline(self):
        global items, objs
        item = self.scene.selectedItems()
        for i in item:
            self.scene.removeItem(i)
            idx = items.index(i)
            items.pop(idx)
            objs.pop(idx)
        self.draw_boxes()

    def nextimage(self):
        self.savetxt()
        self.img_idx += 1
        if self.img_idx == len(self.img_list):
            self.img_idx = len(self.img_list) - 1
            self.savetxt()
            pass
        else:
            self.img_path = self.img_list[self.img_idx]
            self.set_image()

    def previmage(self):
        self.savetxt()
        self.img_idx -= 1
        if self.img_idx < 0:
            self.img_idx = 0
            self.savetxt()
            pass
        else:
            self.img_path = self.img_list[self.img_idx]
            self.set_image()

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.scaleFactor = 1.0
        self.pixmap.setPixmap(self.org_pix)

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        if self.scaleFactor < 1.0:
            self.scaleFactor = 1.0
        self.g_w = self.scaleFactor * self.org_pix.width()
        self.g_h = self.scaleFactor * self.org_pix.height()
        pix = self.org_pix.scaled(self.g_w, self.g_h)
        self.pixmap.setPixmap(pix)
        self.draw_boxes()
        self.scene.setSceneRect(0, 0, self.g_w, self.g_h)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor >= 1.0)

    def savetxt(self):
        global objs
        write_objs = [' '.join(map(str, i))+'\n' for i in objs]
        with open(re.sub(r'.jpg|.JPG|.png', '.txt', self.img_path), 'w') as f:
            f.writelines(write_objs)

    def copy(self):
        global items, objs
        item = self.scene.selectedItems()
        if len(item) == 1:
            assert type(item[0]) == QGraphicsRectItem
            item = item[0].boundingRect()
            self.c_item_coord = [item.x()+10, item.y()+5, item.width(), item.height()]

    def paste(self):
        global items, objs
        if self.c_item_coord:
            rect_item = QGraphicsRectItem(QRectF(*self.c_item_coord))
            rect_item.setPen(QPen(QColor(Qt.red), line_width, Qt.SolidLine))
            rect_item.setFlags(QGraphicsItem.ItemIsSelectable
                               | QGraphicsItem.ItemIsMovable
                               | QGraphicsItem.ItemSendsGeometryChanges)
            self.scene.addItem(rect_item)
            items.append(rect_item)
            yolo_xy = [0, (self.c_item_coord[0]+self.c_item_coord[2]/2.0)/self.g_w,
                       (self.c_item_coord[1]+self.c_item_coord[3]/2.0)/self.g_h,
                       self.c_item_coord[2]/self.g_w,
                       self.c_item_coord[3]/ self.g_w]
            objs.append(yolo_xy)
            self.draw_boxes()
            self.c_item_coord = None

    def delete_img(self):
        ans = QMessageBox.question(self, "사진 삭제", "사진을 삭제하겠습니까?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ans == QMessageBox.Yes:
            os.remove(self.img_path)
            os.remove(re.sub(r'.jpg|.JPG|.png', '.txt', self.img_path))

            self.img_idx += 1
            if self.img_idx == len(self.img_list):
                self.img_list.remove(self.img_path)
                self.img_idx = len(self.img_list) - 1
                self.img_path = self.img_list[self.img_idx]
                self.close_event()
            else:
                self.img_list.remove(self.img_path)
                self.img_path = self.img_list[self.img_idx]
                self.set_image()
        else:
            pass

    def close_event(self):
        ans = QMessageBox.question(self, "종료 확인", "폴더가 끝났습니다 \n종료하시겠습니까?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if ans == QMessageBox.Yes:
            self.close()
        else:
            pass


class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(GraphicsScene, self).__init__(parent)

        self._start = QPointF()
        self._current_item = None
        self.selectionChanged.connect(self.onSelectionChanged)
        self.item = []

    @pyqtSlot()
    def onSelectionChanged(self):
        global items, objs, rectangle
        self.item = self.selectedItems()

    def mousePressEvent(self, event):
        global rectangle, items, line_width

        if type(self.itemAt(event.scenePos(), QTransform())) != QGraphicsRectItem and \
                type(self.itemAt(event.scenePos(), QTransform())) != QGraphicsEllipseItem:
            self._current_item = QGraphicsRectItem()
            self._current_item.setPen(QPen(Qt.red, line_width, Qt.SolidLine))
            self._current_item.setFlags(QGraphicsItem.ItemIsSelectable
                                        | QGraphicsItem.ItemIsMovable
                                        | QGraphicsItem.ItemSendsGeometryChanges)
            self.addItem(self._current_item)
            items.append(self._current_item)
            self._start = event.scenePos()
            r = QRectF(self._start, self._start)
            self._current_item.setRect(r)

        super(GraphicsScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._current_item is not None:
            self._end = event.scenePos()
            self.end = [self._end.x(),self._end.y()]

            if self._end.x() <= 0:
                self.end[0] = 0
            if self._end.x() >= self.itemsBoundingRect().width():
                self.end[0] = self.itemsBoundingRect().width()-2
            if self._end.y() <= 0:
                self.end[1] = 0
            if self._end.y() >= self.itemsBoundingRect().height():
                self.end[1] = self.itemsBoundingRect().height()-2

            r = QRectF(self._start, QPointF(*self.end)).normalized()
            self._current_item.setRect(r)
        super(GraphicsScene, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        global objs, items
        if self._current_item:
            _bbox = self._current_item.boundingRect()
            c_x, c_y, b_w, b_h = _bbox.center().x(), _bbox.center().y(), _bbox.width(), _bbox.height()
            if b_w > 15 and b_h > 15:
                _img = self.sceneRect().size()
                img_w, img_h = _img.width(), _img.height()
                objs.append([0, c_x/img_w, c_y/img_h, b_w/img_w, b_h/img_h])
            else:
                self.removeItem(self._current_item)
                items.pop(-1)

        self._current_item = None
        if len(self.item) == 1:
            assert type(self.item[0]) == QGraphicsRectItem
            area = self.item[0].sceneBoundingRect().getRect()
            img_w, img_h = self.sceneRect().width(), self.sceneRect().height()
            item_idx = items.index(self.item[0])
            objs[item_idx] = [0, (area[0] + area[2] / 2.0) / img_w, (area[1] + area[3]/ 2.0) / img_h,
                              area[2] / img_w, area[3] / img_h]
        super(GraphicsScene, self).mouseReleaseEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    rect = screen.availableGeometry()
    a = Dragger(rect.width(), rect.height())
    sys.exit(app.exec_())
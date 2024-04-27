from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QCheckBox, QVBoxLayout, QPushButton, QMenu, QRubberBand, QFrame
from PyQt6.QtGui import QPixmap, QGuiApplication, QColor, QPainter, QPen, QAction, QBrush
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
import sys
import os
import shutil
from datetime import datetime

# Путь к папке для хранения временных файлов
TEMP_PATH = '.\\temp\\'

os.makedirs(TEMP_PATH)

# Временный список для сохранения в него адресов файлов
images_list = [] 

# Указатель позиции картинки в списке
current_image = 0

# Стартовое окно создания скриншота
class screenshot_start_window(QWidget):
    def __init__(self, main_window, out_label, out_label_2):
        super(screenshot_start_window, self).__init__()
        self.main = main_window
        self.setMinimumSize(300, 50)
        self.out_label = out_label
        self.out_label_2 = out_label_2
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowTitle("Создание скриншота")
        layout = QVBoxLayout()
        btn_make_screenshot = QPushButton('Сделать скриншот')
        layout.addWidget(btn_make_screenshot)
        btn_make_screenshot.clicked.connect(self.make_screenshot)
        self.setLayout(layout)
        self.dim_screen = capture_screen(self.main, self.out_label, self.out_label_2)

    def make_screenshot(self):
        # global images_list, current_image
        self.hide()
        self.main.hide()
        self.dim_screen.show()
        # self.main.show()



class edit_window(QWidget):
    def __init__(self, screen_shot, pict_width, pict_height, file_name, main_window, out_label, out_label_2):
        super(edit_window, self).__init__()
        self.main = main_window
        self.out_label = out_label
        self.out_label_2 = out_label_2
        self.m_width = pict_width
        self.m_height = pict_height + 100
        self.setWindowTitle("Редактирование скриншота")
        self.setMinimumSize(self.m_width, self.m_height)
        layout = QVBoxLayout()
        # self.label = QLabel('Edit image')
        # layout.addWidget(self.label)
        # self.label_1 = QLabel()

        # Размещение кнопки Сохранить
        self.btn_save = QPushButton('Сохранить')
        layout.addWidget(self.btn_save)
        self.btn_save.clicked.connect(self.launchDialog_save)

        # Размещение кнопки Отменить
        self.btn_cancel = QPushButton('Отмена')
        layout.addWidget(self.btn_cancel)
        self.btn_cancel.clicked.connect(self.launchDialog_cancel)

        self.y = screen_shot
        self.file_name = file_name
        # pixmap = QPixmap(self.y)

        # self.label_1.setPixmap(pixmap)
        # layout.addWidget(self.label_1)
        # self.setLayout(layout)
        self.previousPoint = None
        self.label = QLabel()

        self.canvas = QPixmap(self.y)
        

        self.pen = QPen() 
        self.pen.setWidth(6)
        self.pen.setColor(QColor("#ff458b"))
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        self.label.setPixmap(self.canvas)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def mouseMoveEvent(self, event):
        global current_image, images_list
        position = event.pos()

        painter = QPainter(self.canvas)
        painter.setPen(self.pen)
        if self.previousPoint:
            painter.drawLine(self.previousPoint.x()-10, self.previousPoint.y()-80, position.x()-10, position.y()-80)
        else:
            painter.drawPoint(position.x()-10, position.y()-80)

        painter.end()
        self.label.setPixmap(self.canvas)

        self.previousPoint = position

    def mouseReleaseEvent(self, event):
	    self.previousPoint = None    
    
    def launchDialog_save(self):
        global current_image, images_list
        self.main.show()
        self.canvas.save(self.file_name, 'png')
        if len(images_list) == 0:
            images_list.append(self.file_name)
        else:
            if current_image == len(images_list) - 1:
                images_list.append(self.file_name)
                current_image += 1
            else:
                images_list.insert(current_image + 1, self.file_name)
                current_image += 1
        screenshooter.show()
        self.hide()
        pixmap = QPixmap(images_list[current_image])
        self.out_label.setPixmap(pixmap)
        self.out_label_2.setText('Изображение ' + str(current_image+1) + ' из ' + str(len(images_list)))

    def launchDialog_cancel(self):
        screenshooter.show()
        self.hide()
   

class capture_screen(QWidget):
    """Выделение области для создания скриншота"""

    
    # def __init__(self, main_window, label, label_x, images_list, current_image):
    def __init__(self, main_window, out_label, out_label_2):
        super(capture_screen, self).__init__()
        self.main = main_window

        self.origin = QPoint(0,0)
        self.end = QPoint(0,0)
        self.out_label = out_label
        self.out_label_2 = out_label_2
        # self.label = label
        # self.label_x = label_x
        # self.images_list = images_list
        # self.current_image = current_image
 
        self.rubberBand = QRubberBand(QRubberBand.Shape.Rectangle, self) 
        self.create_dim_screen()
        

         
    def create_dim_screen(self):
        """Затемненный экран для выделения области скриншота"""

        primScreenGeo = QGuiApplication.primaryScreen().geometry() 
        screenPixMap = QPixmap(primScreenGeo.width(), primScreenGeo.height())
        screenPixMap.fill(QColor(0,0,0))
        lay = QVBoxLayout()
        self.setLayout(lay)
        self.label1 = QLabel()
        lay.addWidget(self.label1)
        self.label1.setPixmap(screenPixMap)       
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setWindowOpacity(0.4)


    def mousePressEvent(self, event):
        """Начало выделения"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos() 
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

 
    def mouseMoveEvent(self, event):
        """Перемещения курсора для создания прямоугольника выделения"""
        self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

 
    def mouseReleaseEvent(self, event):
        """Обработчик события отпуская клавиши мыши, создание картинки, сохранение её и помещение на рабочий экран"""
        global current_image, images_list
        if event.button() == Qt.MouseButton.LeftButton:
            self.end = event.pos() 
            self.rubberBand.hide()
            self.hide() 
            primaryScreen = QGuiApplication.primaryScreen()
            
            # Создание скриншота и сохранение его во временной папке
            file_name = TEMP_PATH + datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.png'
            if self.origin.x() < self.end.x() and self.origin.y() < self.end.y():
                grabbedPixMap = primaryScreen.grabWindow(0, self.origin.x(), self.origin.y(), self.end.x()-self.origin.x(), self.end.y()-self.origin.y())
                # grabbedPixMap.save(file_name, 'png')
            elif self.origin.x() > self.end.x() and self.origin.y() < self.end.y():
                grabbedPixMap = primaryScreen.grabWindow(0, self.end.x(), self.origin.y(), self.origin.x()-self.end.x(), self.end.y()-self.origin.y())
                # grabbedPixMap.save(file_name, 'png')
            elif self.origin.x() < self.end.x() and self.origin.y() > self.end.y():
                grabbedPixMap = primaryScreen.grabWindow(0, self.origin.x(), self.end.y(), self.end.x()-self.origin.x(), self.origin.y()-self.end.y())
                # grabbedPixMap.save(file_name, 'png')
            elif self.origin.x() > self.end.x() and self.origin.y() > self.end.y():
                grabbedPixMap = primaryScreen.grabWindow(0, self.end.x(), self.end.y(), self.origin.x()-self.end.x(), self.origin.y()-self.end.y())
                # grabbedPixMap.save(file_name, 'png')

            self.x = edit_window(grabbedPixMap, grabbedPixMap.width(), grabbedPixMap.height(), file_name, self.main, self.out_label, self.out_label_2)
        
            self.x.show()
            # self.label.setPixmap(pixmap)
            # self.label_x.setText('Изображение ' + str(current_image+1) + ' из ' + str(len(images_list)))
        
            
# Настройка основного рабочего окна
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Настройка окна
        # self.m_width = x_x
        # self.m_height = y_y
        self.setWindowTitle("Screen Scissors")
        # self.setMinimumSize(self.m_width, self.m_height)
        frame = QFrame()
        frame.setContentsMargins(0, 0, 0, 0)
        
        self.pixmap = QPixmap()
        # Настройка контекстного меню
        self.context_menu = QMenu(self)
        action1 = self.context_menu.addAction("Удалить")
        action1.triggered.connect(self.action1_triggered)

        # Настройка рабочего слоя
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(5, 5, 5, 5)

        # Размещение кнопки предыдущая картинка
        self.btn_previous = QPushButton('Предыдущая')
        layout.addWidget(self.btn_previous)
        self.btn_previous.clicked.connect(self.launchDialog_prev)

        # Размещение кнопки загрузки файла
        btn_capture_screen = QPushButton('Сделать скриншот')
        layout.addWidget(btn_capture_screen)
        btn_capture_screen.move(100, 10)
        btn_capture_screen.clicked.connect(self.screen_capture)

        # Размещение кнопки следующая картинка
        btn_next = QPushButton('Следующая')
        layout.addWidget(btn_next)
        btn_next.clicked.connect(self.launchDialog_next)       

        # btn_edit = QPushButton('Edit')
        # layout.addWidget(btn_edit)
        # btn_edit.clicked.connect(self.edit_start)

        # Размещение места для картинки
        self.label_x = QLabel()
        layout.addWidget(self.label_x)
        self.label = QLabel()
        layout.addWidget(self.label)
        # self.setLayout(layout)
        # if len(images_list) != 0:
        #     pixmap = QPixmap(images_list[current_image])
        #     self.label_x.setText('Изображение ' + str(current_image+1) + ' из ' + str(len(images_list)))  
        # else:
        #     pixmap = QPixmap()      

        self.label.setPixmap(self.pixmap)
        # self.label.setPixmap(pixmap)
        # self.label_x.setText('Изображение ' + str(current_image+1) + ' из ' + str(len(images_list)))
        # Размещение чек-бокса режима "Поверх всех окон"
        self.ontop_checkbox = QCheckBox("Поверх окон", self)
        layout.addWidget(self.ontop_checkbox)
        self.ontop_checkbox.stateChanged.connect(self.the_checkbox_clicked)
        # self.ontop_checkbox.move(100, 10)
        # self.ontop_checkbox.resize(320, 40) 

        # Создание объекта-обработчика скриншотов
        # self.dim_screen = capture_screen(self, self.label, self.label_x, images_list, current_image)
        self.screenshot_window = screenshot_start_window(self, self.label, self.label_x)

        # self.edit_screen = edit_window(pixmap, pixmap.width(), pixmap.height())
        self.setCentralWidget(frame)


    # Функция запуска создателя скриншота
    def screen_capture(self):
        global images_list, current_image
        # self.hide()
        # self.dim_screen.show()
        self.screenshot_window.show()
        print(images_list)

    def edit_start(self):
        self.edit_screen = edit_window(self.label.pixmap(), self.label.pixmap().width(), self.label.pixmap().height(), file_name)
        self.edit_screen.show()
 

    # Функция запуска контекстного меню
    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

 
    # Функция удаления картинки
    def action1_triggered(self):
        global images_list, current_image
        if len(images_list) == 1:
            pixmap = QPixmap()
            # self.label.setPixmap(pixmap)
            # self.label.move(100, 100)
        elif current_image == len(images_list) - 1:
            del images_list[current_image]
            current_image -= 1
            pixmap = QPixmap(images_list[current_image])
            # self.label.setPixmap(pixmap)

        else:
            del images_list[current_image]
            pixmap = QPixmap(images_list[current_image])
        self.label.setPixmap(pixmap)
        self.label_x.setText('Изображение ' + str(current_image+1) + ' из ' + str(len(images_list)))


    # Функция помещения рабочего окна поверх всех окон
    def the_checkbox_clicked(self, state):
        if Qt.CheckState(state) == Qt.CheckState.Checked:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnBottomHint, False)  
            self.show()
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self.show()
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            self.show()
        self.show() 


    # Функция демонстрации предыдущей картинки
    def launchDialog_prev(self):
        global images_list, current_image
        if current_image > 0:
            current_image -= 1
            pixmap = QPixmap(images_list[current_image])
            self.label.setPixmap(pixmap)
            self.label_x.setText('Изображение ' + str(current_image+1) + ' из ' + str(len(images_list)))


    # Функция демонстрации следующей картинки
    def launchDialog_next(self):
        global images_list, current_image
        if current_image < len(images_list) - 1:
            current_image += 1
            pixmap = QPixmap(images_list[current_image])            
            self.label.setPixmap(pixmap)
            self.label_x.setText('Изображение ' + str(current_image+1) + ' из ' + str(len(images_list)))

class marker():
    def __init__(self):
        super(marker, self).__init__()
        self.marker = 0

marker_1 = marker()



# Основное тело программы
if __name__ == "__main__":
    app = QApplication(sys.argv)  
    scissors = Window()
    screenshooter = screenshot_start_window(scissors, scissors.label, scissors.label_x)
    if marker_1.marker == 0:
        # screenshooter = screenshot_start_window(scissors, scissors.label, scissors.label_x)
        # scissors.show()
        screenshooter.show()
    else:
        scissors.show()


    app.exit(app.exec())
    shutil.rmtree(TEMP_PATH)

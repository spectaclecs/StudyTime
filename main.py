import datetime

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QTime
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLCDNumber, QHeaderView
from qfluentwidgets import *
import sys


class Window(FluentWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.resize(1000, 600)
        self.setWindowTitle('Study Time')
        self.setWindowIcon(QIcon('icon-alram.svg'))
        # self.setWindowIcon(QIcon('favicon.ico'))

        layoutWidget = QtWidgets.QWidget(self)
        layout = QtWidgets.QGridLayout(layoutWidget)
        layoutWidget.setLayout(layout)
        layoutWidget.setGeometry(QtCore.QRect(200, 100, 600, 400))

        self.start_button = PrimaryPushButton("start", layoutWidget)
        self.stop_button = PrimaryPushButton("stop", layoutWidget)


        self.timer = QtCore.QTimer(self)

        # self.time_picker = TimeEdit()
        # self.time_picker.setTime(QTime(0, 0, 0))
        # self.time_picker.setReadOnly(True)
        # self.time_picker.setDisplayFormat('hh : mm : ss')
        # self.time_picker.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        # self.time_picker.setFont(QtGui.QFont())
        # layout.addWidget(self.time_picker, 2, 1)

        self.lcd = QtWidgets.QLCDNumber(layoutWidget)
        self.lcd.setDigitCount(12)

        self.lcd.display('00:00:00.00')

        self.time = QtCore.QTime(0, 0, 0)

        self.table = TableWidget(layoutWidget)
        self.table.setColumnCount(4)
        # self.table.setRowCount(3)
        self.table.setHorizontalHeaderLabels(['开始时间', '结束时间', '时长', '总时间'])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.)
        # self.table.resizeColumnsToContents()

        layout.addWidget(self.start_button, 0, 3, 1, 4)
        layout.addWidget(self.stop_button, 1, 3, 1, 4)
        layout.addWidget(self.lcd, 2, 0, 2, 10)
        layout.addWidget(self.table, 4, 1, 2, 8)

        self.start_button.clicked.connect(lambda: click_start(self.timer))
        self.stop_button.clicked.connect(lambda: click_end(self.timer, self.table))
        self.timer.timeout.connect(lambda: refresh_time(self, self.lcd))


start_time: QTime = None
cumulative_time: QTime = QTime(0, 0, 0, 0)


def click_start(timer: QtCore.QTimer):
    timer.start(10)
    global start_time
    start_time = QTime.currentTime()


def click_end(timer: QtCore.QTimer, table: TableWidget):
    global start_time
    global cumulative_time
    if start_time is not None:
        current_row_count = table.rowCount()
        table.insertRow(current_row_count)
        table.setItem(current_row_count, 0, QtWidgets.QTableWidgetItem(start_time.toString('hh : mm : ss')))
        end_time: QTime = QTime.currentTime()
        cumulative_time = cumulative_time.addMSecs(start_time.msecsTo(end_time))
        table.setItem(current_row_count, 1, QtWidgets.QTableWidgetItem(end_time.toString('hh : mm : ss')))
        table.setItem(current_row_count, 2, QtWidgets.QTableWidgetItem(QTime(0, 0, 0).addSecs(start_time.secsTo(end_time)).toString('hh : mm : ss')))
        table.setItem(current_row_count, 3, QtWidgets.QTableWidgetItem(cumulative_time.toString('hh : mm : ss')))
        # table.verticalScrollBar().setValue(table.verticalScrollBar().maximum())
        start_time = None
        timer.stop()


def refresh_time(window: Window, lcd: QLCDNumber):
    global cumulative_time
    global start_time
    window.time = cumulative_time.addMSecs(start_time.msecsTo(QTime.currentTime()))
    if window.time.msec() % 10 != 0:
        lcd.display(window.time.toString('hh:mm:ss.zz')[0:11])
    elif window.time.msec() // 10 % 10 == 0:
        lcd.display(window.time.toString('hh:mm:ss.zz') + '0')
    else:
        lcd.display(window.time.toString('hh:mm:ss.zz'))


def timedelta2str(td: datetime.timedelta) -> str:
    seconds = td.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02} : {int(minutes):02} : {int(seconds):02}"


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
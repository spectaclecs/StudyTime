import datetime

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QTime
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLCDNumber, QHeaderView
from qfluentwidgets import *
import sys
import os


class Window(FluentWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.resize(1000, 700)
        self.setWindowTitle('Study Time')
        self.setWindowIcon(QIcon('icon-alram.svg'))
        # self.setWindowIcon(QIcon('favicon.ico'))

        layoutWidget = QtWidgets.QWidget(self)
        layout = QtWidgets.QGridLayout(layoutWidget)
        layoutWidget.setLayout(layout)
        layoutWidget.setGeometry(QtCore.QRect(200, 100, 600, 500))

        self.start_button = PrimaryPushButton("start", layoutWidget)
        self.stop_button = PrimaryPushButton("stop", layoutWidget)

        self.timer = QtCore.QTimer(self)
        self.lcd = QtWidgets.QLCDNumber(layoutWidget)
        self.lcd.setDigitCount(12)

        self.lcd.display('00:00:00.00')

        self.time = QtCore.QTime(0, 0, 0)

        self.table = TableWidget(layoutWidget)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['开始时间', '结束时间', '时长', '总时间'])
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.)
        # self.table.resizeColumnsToContents()

        self.clear_button = PrimaryPushButton("clear", layoutWidget)

        layout.addWidget(self.start_button, 0, 3, 1, 4)
        layout.addWidget(self.stop_button, 1, 3, 1, 4)
        layout.addWidget(self.lcd, 2, 0, 2, 10)
        layout.addWidget(self.table, 4, 1, 2, 8)
        layout.addWidget(self.clear_button, 6, 3, 1, 4)

        self.start_button.clicked.connect(lambda: click_start(self.timer))
        self.stop_button.clicked.connect(lambda: click_end(self.timer, self.table))
        self.timer.timeout.connect(lambda: refresh_time(self, self.lcd))
        self.clear_button.clicked.connect(lambda: clear(self))

        records = read_log()
        total_time_str = None
        for record in records:
            add2table(self.table, *record)
            total_time_str = record[-1]
        if total_time_str is not None:
            cumulative_time = QTime.fromString(total_time_str, 'hh : mm : ss . zzz')
            display_lcd(cumulative_time, self.lcd)


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
        end_time: QTime = QTime.currentTime()
        cumulative_time = cumulative_time.addMSecs(start_time.msecsTo(end_time))
        str0 = start_time.toString('hh : mm : ss')
        str1 = end_time.toString('hh : mm : ss')
        str2 = QTime(0, 0, 0).addSecs(start_time.secsTo(end_time)).toString('hh : mm : ss')
        str3 = cumulative_time.toString('hh : mm : ss . zzz')
        add2table(table, str0, str1, str2, str3)
        # table.verticalScrollBar().setValue(table.verticalScrollBar().maximum())
        write_log(str0 + ',' + str1 + ',' + str2 + ',' + str3)
        start_time = None
        timer.stop()


def clear(window: Window):
    global start_time
    global cumulative_time
    w = Dialog("Attention", "Are you sure to clear today's log?", window)
    if w.exec():
        start_time = None
        cumulative_time = QTime(0, 0, 0, 0)
        display_lcd(cumulative_time, window.lcd)
        window.table.setRowCount(0)
        today = datetime.date.today()
        path = 'log/' + str(today) + '.log'
        if os.path.exists(path):
            with open(path, 'w') as file:
                file.truncate(0)


def add2table(table: TableWidget, *items):
    current_row_count = table.rowCount()
    table.insertRow(current_row_count)
    for i, item in enumerate(items):
        table.setItem(current_row_count, i, QtWidgets.QTableWidgetItem(item[0:12]))


def refresh_time(window: Window, lcd: QLCDNumber):
    global cumulative_time
    global start_time
    window.time = cumulative_time.addMSecs(start_time.msecsTo(QTime.currentTime()))
    display_lcd(window.time, lcd)


def display_lcd(time: QTime, lcd: QLCDNumber):
    if time.msec() % 10 != 0:
        lcd.display(time.toString('hh:mm:ss.zz')[0:11])
    elif time.msec() // 10 % 10 == 0:
        lcd.display(time.toString('hh:mm:ss.zz') + '0')
    else:
        lcd.display(time.toString('hh:mm:ss.zz'))


def timedelta2str(td: datetime.timedelta) -> str:
    seconds = td.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02} : {int(minutes):02} : {int(seconds):02}"


def write_log(string):
    today = datetime.date.today()
    path = 'log/' + str(today) + '.log'
    if os.path.exists(path):
        with open(path, 'a') as file:
            print(string, file=file)


def read_log():
    ret = []
    today = datetime.date.today()
    path = 'log/' + str(today) + '.log'
    if not os.path.exists(path):
        if not os.path.exists('log'):
            os.mkdir('log')
        open(path, 'a').close()
    with open(path) as file:
        # Dialog("log file error", "Log file corrupted, are you sure to clear today's logfile?", window)
        for line in file:
            ret.append(line.strip().split(','))
    return ret


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
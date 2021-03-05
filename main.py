import traceback
from threading import Thread

import requests
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QLabel
from PyQt5.QtCore import pyqtSignal, QObject, QDate
from time import sleep

from ui import mainWindow
from app import getClassData
from app import timetableMaker


class MySignals(QObject):
    error_print = pyqtSignal(str)
    msg_print = pyqtSignal(str)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = mainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("ICS生成小工具")
        # 设置超链
        self.ui.link.setText(u'<a href="https://blog.csdn.net/qq_45355034/article/details/113103504" style="color:#0000ff;"><b> 右键此处,选择复制教程网址（Copy Link Location）,到浏览器打开 </b></a>')
        # 一些变量
        self.username = ''
        self.password = ''
        self.xnm = ''
        self.xqm = ''
        self.classInfoList = ''
        self.flag = ''
        self.date = ''
        self.reminder = ''
        # 一些实例化
        self.global_ms = MySignals()
        self.msgBox = QMessageBox()
        # 绑定信号与槽
        self.ui.workOut.clicked.connect(self.doMain)
        self.global_ms.error_print.connect(self.showErrorMsgBox)
        self.ui.calendarWidget.clicked[QDate].connect(self.printDateToDateShower)
        self.ui.checkDate.clicked.connect(self.checkDate)
        self.ui.buttonGroup.buttonClicked.connect(self.getReminder)

    def doMain(self):
        # 读取参数
        self.username = self.ui.username.text()
        self.password = self.ui.password.text()
        self.xnm = self.ui.xnm.currentText()
        self.xqm = self.ui.xqm.currentText()
        # 处理参数
        self.xnm = self.xnm.split('-')[0]
        if self.xqm == '春季学期':
            self.xqm = 12
        else:
            self.xqm = 3
        # 获取课表
        # 涉及HTTP请求，新建一个线程处理
        thread_1 = Thread(target=self.threadFunc_1, daemon=True)
        thread_1.start()

    def printStrToGui(self, string):
        self.ui.shower.setText(string)

    def printStrToCheckShower(self, string):
        self.ui.checkShower.setText(string)

    def printDateToDateShower(self, date):
        self.printStrToCheckShower('未确认')
        self.date = ''
        self.ui.dataShower.setText(date.toString('yyyy-MM-dd'))

    def threadFunc_1(self):
        try:
            # 检查所需参数是否完整
            # 注意 self.reminder 可能取 0
            if self.date and self.reminder != '' and self.username and self.password and self.xnm and self.xqm:
                # shower 的循环播报
                thread_2 = Thread(target=self.threadFunc_2, args=("正在查询课表并生成ics文件",), daemon=True)
                thread_2.start()
                # 查询课程表
                self.classInfoList = getClassData.GetClassData(self.username, self.password, self.xnm, self.xqm).main()
                # 生成ics文件
                timetableMaker.TimetableMaker(self.classInfoList, self.reminder, self.date).main()
                # 发出消息
                self.flag = False
                self.printStrToGui("已在同级目录下生成ics文件成功")
            else:
                self.global_ms.error_print.emit("请不要遗漏所需信息")
        except requests.exceptions.ConnectionError:
            self.global_ms.error_print.emit("网络错误，校外用户请检查是否连接VPN")
        except getClassData.LoginException:
            self.global_ms.error_print.emit("登录错误，请检查用户名或密码。\n若确认无误，请检查：\n1.aes.js文件是否在同一文件夹下\n2.前往学校融合门户 http://authserver.cumt.edu.cn/authserver/login，输入学号，检查是否需要输入验证码")
        except getClassData.SpiderException:
            self.global_ms.error_print.emit("没有查到课表，请检查所提供的信息")
        except Exception as e:
            print(traceback.format_exc())
            self.global_ms.error_print.emit("出现错误，请联系开发者")

    def threadFunc_2(self, msg):
        # shower 的循环处理
        self.flag = True
        i = 1
        # 循环不能放在主线程中，必须新开一个线程
        while self.flag:
            string = msg + "." * i
            i = i + 1
            if i == 4:
                i = 0
            self.printStrToGui(string)
            sleep(1)

    def showErrorMsgBox(self, msg):
        self.flag = False
        self.msgBox.critical(self, '错误', msg)

    def checkDate(self):
        self.date = self.ui.calendarWidget.selectedDate().toString("yyyyMMdd")
        self.printStrToCheckShower('已确认')

    def getReminder(self, button):
        msg = button.text()
        if msg == '不提醒':
            self.reminder = 0
        elif msg == '上课前 10 分钟提醒':
            self.reminder = 1
        elif msg == '上课前 30 分钟提醒':
            self.reminder = 2
        elif msg == '上课前 1 小时提醒':
            self.reminder = 3
        elif msg == '上课前 2 小时提醒':
            self.reminder = 4
        elif msg == '上课前 1 天提醒':
            self.reminder = 5


if __name__ == '__main__':
    app = QApplication([])
    mainW = MainWindow()
    mainW.show()
    app.exec_()

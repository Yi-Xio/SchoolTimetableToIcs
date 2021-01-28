import requests
from bs4 import BeautifulSoup

import time, datetime
from random import Random
import json
import copy
import re
from os import system


class GetClassData(object):

    def login(self):

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.50"
        }

        form = {
            "username": self.username,
            "password": self.password,
            "signIn": ""
        }

        url_index = "http://ids.cumt.edu.cn/authserver/login?service=http%3A%2F%2Fmy.cumt.edu.cn%2Flogin.portal"
        url_jw_index = "http://jiaowujizhong.cumt.edu.cn:8080/jwjz/"
        url_jwxt = "http://jwxt.cumt.edu.cn/sso/jzIdsFivelogin"

        self.session = requests.session()
        resp = self.session.get(url=url_index, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'lxml')
        blocks = soup.find_all(type="hidden")
        for block in blocks[:-1]:
            form[block["name"]] = block["value"]
        resp = self.session.post(url=url_index, headers=self.headers, data=form)
        resp = self.session.get(url=url_jw_index, headers=self.headers)
        resp = self.session.get(url=url_jwxt, headers=self.headers)

    def spider(self):
        # 构建url
        username = self.username
        url = "http://jwxt.cumt.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N253508&su=" + username
        # 构建form
        xnm = input("请输入待查询学年（如2020-2021学年输入2020）：")
        xqm = input("请输入待查学期（如春季学期输入12，秋季学期输入3）：")
        form ={
            "xnm":xnm,
            "xqm":xqm
        }
        # 请求
        response = self.session.post(url=url, data=form, headers=self.headers)
        data = response.json()
        if data:
        # 处理json
            classDataList = []
            kbList = data["kbList"]
            for kb in kbList:
                classInfo = {}
                classInfo["className"] = kb["kcmc"] 
                classInfo["classroom"] = kb["cdmc"] 
                weekday_str = kb["xqjmc"]
                if weekday_str == "星期一":
                    weekday = 1
                elif weekday_str == "星期二":
                    weekday = 2
                elif weekday_str == "星期三":
                    weekday = 3
                elif weekday_str == "星期四":
                    weekday = 4
                elif weekday_str == "星期五":
                    weekday = 5
                classInfo["weekday"] = weekday 
                classTime_str = kb["jc"]
                if classTime_str == "1-2节":
                    classTime = 1
                elif classTime_str == "3-4节":
                    classTime = 2
                elif classTime_str == "5-6节":
                    classTime = 3
                elif classTime_str == "7-8节":
                    classTime = 4
                elif classTime_str == "9-10节":
                    classTime = 5
                classInfo["classTime"] = classTime 

                weeks = kb["zcd"].split(",")
                for week in weeks:
                    # print(week)
                    # 参天巨坑！！！ copy.deepcopy
                    classInfo_new = copy.deepcopy(classInfo)
                    # 处理情况一：“9-11周(单)” 只有单周上课
                    if re.search("单", week):
                        startWeek = week.split("-")[0]
                        endWeek = week.split("-")[1]
                        cop = re.compile("\D") 
                        startWeek = int(cop.sub('', startWeek))
                        endWeek = int(cop.sub('', endWeek))
                        # 确保 startWeek 为单周
                        if startWeek % 2 == 0:
                            startWeek += 1
                        # 开始生成
                        for iWeek in range(startWeek, endWeek+1, 2):
                            iclassInfo_new = copy.deepcopy(classInfo)
                            iclassInfo_new["week"] = {
                                "startWeek":str(iWeek),
                                "endWeek":str(iWeek)
                            }
                            classDataList.append(iclassInfo_new)
                    # 处理情况二：“9-11周(双)” 只有双周上课
                    elif re.search("双", week):
                        startWeek = week.split("-")[0]
                        endWeek = week.split("-")[1]
                        cop = re.compile("\D") 
                        startWeek = int(cop.sub('', startWeek))
                        endWeek = int(cop.sub('', endWeek))
                        # 确保 startWeek 为双周
                        if startWeek % 2 != 0:
                            startWeek += 1
                        # 开始生成
                        for iWeek in range(startWeek, endWeek+1, 2):
                            iclassInfo_new = copy.deepcopy(classInfo)
                            iclassInfo_new["week"] = {
                                "startWeek":iWeek,
                                "endWeek":iWeek
                            }
                            classDataList.append(iclassInfo_new)
                    else:
                        # 处理情况三：“9-11周” 正常情况
                        if len(week.split("-")) == 2:
                            # print((week.split("-")))
                            startWeek = week.split("-")[0]
                            # 利用正则，只保留str中的数字
                            cop = re.compile("\D") # 匹配不是中文、大小写、数字的其他字符
                            startWeek = cop.sub('', startWeek) #将str匹配到的字符替换成空字符
                            endWeek = week.split("-")[1]
                            cop = re.compile("\D") 
                            endWeek = cop.sub('', endWeek) 
                            classInfo_new["week"] = {
                                "startWeek":startWeek,
                                "endWeek":endWeek
                            }
                            classDataList.append(classInfo_new)
                        # 处理情况四：“11周” 只有一周
                        elif len(week.split("-")) == 1:
                            startWeek = week.split('"')[0][:-1]
                            cop = re.compile("\D") 
                            startWeek = cop.sub('', startWeek) 
                            classInfo_new["week"] = {
                                "startWeek":startWeek,
                                "endWeek":startWeek
                            }
                            classDataList.append(classInfo_new)    
            # print(classDataList)
            return classDataList
        else:
            print("爬取结果为空，请检查参数是否正确")
            raise Exception("爬虫参数错误")

    def main(self):
        print("开始爬取课程表。校外用户记得挂VPN")
        self.username = input("请输入学号:")
        self.password = input("请输入旧版统一身份认证（http://ids.cumt.edu.cn/authserver/login）密码:")
        print("正在尝试模拟登录，校外用户务必挂上VPN")
        self.login()
        print("模拟登陆成功")
        classDataList = self.spider()
        print("爬取课表成功！")
        return classDataList
        

class CheckTools(object):
    # 对输入的数据进行检查，检查通过的返回数据，否则要求重新输入
    def checkInput(self, checkType, data):
        if(checkType == 1):     # 检查第一周星期一输入格式
            if (not self.checkFirstWeekDate(data)):
                data = input("输入有误，请重新输入第一周的星期一日期(如：20210301):")
                self.checkInput(1, data)
            else:
                return data
        elif(checkType == 2):       # 检查是否设置上课提醒
            if(not self.checkReminder(data)):
                data = input("输入有误，请重新输入\n【1】上课前 10 分钟提醒\n【2】上课前 30 分钟提醒\n【3】上课前 1 小时提醒\n【4】上课前 2 小时提醒\n【5】上课前 1 天提醒\n")
                self.checkInput(2, data)
            else:
                return data

    def checkFirstWeekDate(self, firstWeekDate):
        flag = True
        # 长度判断
        if(len(firstWeekDate) != 8):
            flag = False
        # 切割输入数据
        year = firstWeekDate[0:4]
        month = firstWeekDate[4:6]
        date = firstWeekDate[6:8]
        # 年份判断
        if(int(year) < 1970):
            flag = False
        # 月份判断
        if(int(month) == 0 or int(month) > 12):
            flag = False
        # 日期判断
        dateList = [31,29,31,30,31,30,31,31,30,31,30,31]
        if(int(date) > dateList[int(month)-1]):
            flag = False
        # 返回检查结果
        return flag

    def checkReminder(self, reminder):
        List = ["0","1","2","3","4","5"]
        if reminder in List:
            return True
        else:
            return False


class TimetableMaker(object):

    # 配置生成相关信息
    def data_load(self):
        print("为了生成课表ics文件，请提供以下信息：")
        firstWeekDate = input("请设置第一周的星期一日期(如：20210301):")
        # 检查输入数据
        firstWeekDate = CheckTools().checkInput(1, firstWeekDate)
        # 设置第一周星期一日期
        self.DONE_firstWeekDate = time.strptime(firstWeekDate,'%Y%m%d')
        # 设置上课时间
        self.classTimeList = [
            {
                "name":"第 1-2 节",
                "startTime":"0800",
                "endTime":"0945"
            },
            {
                "name":"第 3-4 节",
                "startTime":"1015",
                "endTime":"1200"
            },
            {
                "name":"第 5-6 节",
                "startTime":"1400",
                "endTime":"1545"
            },
            {
                "name":"第 7-8 节",
                "startTime":"1615",
                "endTime":"1800"
            },
            {
                "name":"第 9-10 节",
                "startTime":"1900",
                "endTime":"2045"
            }
        ]
        # 设置上课提醒
        reminder = input("请输入数字选择上课提醒时间\n【0】不提醒\n【1】上课前 10 分钟提醒\n【2】上课前 30 分钟提醒\n【3】上课前 1 小时提醒\n【4】上课前 2 小时提醒\n【5】上课前 1 天提醒\n请输入你的选项：")
        reminder = CheckTools().checkInput(2, reminder)
        if(reminder == "1"):
            self.DONE_reminder = "-PT10M"
        elif(reminder == "2"):
            self.DONE_reminder = "-PT30M"
        elif(reminder == "3"):
            self.DONE_reminder = "-PT1H"
        elif(reminder == "4"):
            self.DONE_reminder = "-PT2H"
        elif(reminder == "5"):
            self.DONE_reminder = "-P1D"
        else:
            self.DONE_reminder = "NULL"

    # 单元设置
    def uniteSetting(self):
        self.DONE_ALARMUID = self.random_str(30) + "&yzj"
        self.DONE_UnitUID = self.random_str(20) + "&yzj"

    def random_str(self, randomlength):
        str = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        length = len(chars) - 1
        random = Random()
        for i in range(randomlength):
            str+=chars[random.randint(0, length)]
        return str

    # 处理课程信息
    def classInfoHandle(self):
        self.classList = []
        for classInfo in self.classInfoList:
            # 具体日期计算出来
            startWeek = json.dumps(classInfo["week"]["startWeek"])
            endWeek = json.dumps(classInfo["week"]["endWeek"])
            weekday = float(json.dumps(classInfo["weekday"]))
            
            # print(classInfo)
            dateLength = float((int(startWeek[1:-1]) - 1) * 7)
            startDate = datetime.datetime.fromtimestamp(int(time.mktime(self.DONE_firstWeekDate))) + datetime.timedelta(days = dateLength + weekday - 1)
            string = startDate.strftime('%Y%m%d')

            dateLength = float((int(endWeek[1:-1]) - 1) * 7)
            endDate = datetime.datetime.fromtimestamp(int(time.mktime(self.DONE_firstWeekDate))) + datetime.timedelta(days = dateLength + weekday - 1)
            
            date = startDate
            dateList = []
            dateList.append(string)
            flag = True
            while (flag):
                date = date + datetime.timedelta(days = 7.0)
                if(date > endDate):
                    flag = False
                else:
                    string = date.strftime('%Y%m%d')
                    dateList.append(string)
            classInfo["date"] = dateList

            # 设置 UID
                # 生成 CREATED
            date = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
            self.DONE_CreatedTime = date + "Z"
            classInfo["CREATED"] = self.DONE_CreatedTime
            classInfo["DTSTAMP"] = self.DONE_CreatedTime

            UID_List = []
            for date in dateList:
                UID_List.append(self.random_str(20) + "&yzj")
            classInfo["UID"] = UID_List
            # 写入list
            self.classList.append(classInfo)

        # 写成ics文件并保存ics
    def icsCreateAndSave(self):
        icsString = "BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:3.0\nX-WR-CALNAME:课程表\nPRODID:-//Apple Inc.//Mac OS X 10.12//EN\nX-APPLE-CALENDAR-COLOR:#FC4208\nX-WR-TIMEZONE:Asia/Shanghai\nCALSCALE:GREGORIAN\nBEGIN:VTIMEZONE\nTZID:Asia/Shanghai\nBEGIN:STANDARD\nTZOFFSETFROM:+0900\nRRULE:FREQ=YEARLY;UNTIL=19910914T150000Z;BYMONTH=9;BYDAY=3SU\nDTSTART:19890917T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0800\nEND:STANDARD\nBEGIN:DAYLIGHT\nTZOFFSETFROM:+0800\nDTSTART:19910414T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0900\nRDATE:19910414T000000\nEND:DAYLIGHT\nEND:VTIMEZONE\n"
        eventString = ""
        for classInfo in self.classList :
            i = int(classInfo["classTime"]-1)
            className = classInfo["className"]+"|"+classInfo["classroom"]
            endTime = self.classTimeList[i]["endTime"]
            startTime = self.classTimeList[i]["startTime"]
            index = 0
            for date in classInfo["date"]:
                eventString = eventString+"BEGIN:VEVENT\nCREATED:" + classInfo["CREATED"]
                eventString = eventString+"\nUID:" + classInfo["UID"][index]
                eventString = eventString+"\nDTEND;TZID=Asia/Shanghai:" + date + "T" + endTime
                eventString = eventString+"00\nTRANSP:OPAQUE\nX-APPLE-TRAVEL-ADVISORY-BEHAVIOR:AUTOMATIC\nSUMMARY:" + className
                eventString = eventString+"\nDTSTART;TZID=Asia/Shanghai:" + date +"T" + startTime+"00"
                eventString = eventString+"\nDTSTAMP:" + self.DONE_CreatedTime
                eventString = eventString+"\nSEQUENCE:0\nBEGIN:VALARM\nX-WR-ALARMUID:" + self.DONE_ALARMUID
                eventString = eventString+"\nUID:" + self.DONE_UnitUID
                eventString = eventString+"\nTRIGGER:" + self.DONE_reminder
                eventString = eventString+"\nDESCRIPTION:事件提醒\nACTION:DISPLAY\nEND:VALARM\nEND:VEVENT\n"

                index += 1
        icsString = icsString + eventString + "END:VCALENDAR"
        # print(icsString)
        with open("school_timetable.ics", "w", encoding="utf-8") as f:
            f.write(icsString)
            print("ics文件已生成，请导入日历app中使用")

    def main(self):
        self.classInfoList = GetClassData().main()  # 爬取教务，处理课程信息
        self.data_load()
        self.uniteSetting()
        self.classInfoHandle()
        self.icsCreateAndSave()


if __name__ == '__main__':
    try:
        TimetableMaker().main()
    except requests.exceptions.ConnectionError as e:
        print("网络连接错误，请检查是否挂上VPN")
    except Exception as e:
        print("发生错误,请检查输入参数是否有误")
    finally:
        system("pause")

# TimetableMaker().main()

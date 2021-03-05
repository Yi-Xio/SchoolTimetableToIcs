import datetime
import json
import time
from random import Random


class TimetableMaker(object):

    def __init__(self, classInfoList, reminder, firstWeekDate):
        self.classInfoList = classInfoList
        self.reminder = reminder
        self.firstWeekDate = firstWeekDate

    # 配置生成相关信息
    def data_load(self):
        # 设置第一周星期一日期
        self.DONE_firstWeekDate = time.strptime(self.firstWeekDate, '%Y%m%d')
        # 设置上课时间
        self.classTimeList = [
            {
                "name": "第 1-2 节",
                "startTime": "0800",
                "endTime": "0945"
            },
            {
                "name": "第 3-4 节",
                "startTime": "1015",
                "endTime": "1200"
            },
            {
                "name": "第 5-6 节",
                "startTime": "1400",
                "endTime": "1545"
            },
            {
                "name": "第 7-8 节",
                "startTime": "1615",
                "endTime": "1800"
            },
            {
                "name": "第 9-10 节",
                "startTime": "1900",
                "endTime": "2045"
            }
        ]
        # 设置上课提醒
        if self.reminder == "1":
            self.DONE_reminder = "-PT10M"
        elif self.reminder == "2":
            self.DONE_reminder = "-PT30M"
        elif self.reminder == "3":
            self.DONE_reminder = "-PT1H"
        elif self.reminder == "4":
            self.DONE_reminder = "-PT2H"
        elif self.reminder == "5":
            self.DONE_reminder = "-P1D"
        else:
            self.DONE_reminder = "NULL"

    # 单元设置
    def uniteSetting(self):
        self.DONE_ALARMUID = self.random_str(30) + "&yzj"
        self.DONE_UnitUID = self.random_str(20) + "&yzj"

    def random_str(self, randomlength):
        string = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        length = len(chars) - 1
        random = Random()
        for i in range(randomlength):
            string += chars[random.randint(0, length)]
        return string

    # 处理课程信息
    def classInfoHandle(self):
        self.classList = []
        for classInfo in self.classInfoList:
            # 具体日期计算出来
            startWeek = json.dumps(classInfo["week"]["startWeek"])
            endWeek = json.dumps(classInfo["week"]["endWeek"])
            weekday = float(json.dumps(classInfo["weekday"]))
            # print(classInfo)
            # print(startWeek, endWeek, weekday)
            # print(classInfo)
            dateLength = float((int(startWeek[1:-1]) - 1) * 7)
            startDate = datetime.datetime.fromtimestamp(int(time.mktime(self.DONE_firstWeekDate))) + datetime.timedelta(
                days=dateLength + weekday - 1)
            string = startDate.strftime('%Y%m%d')

            dateLength = float((int(endWeek[1:-1]) - 1) * 7)
            endDate = datetime.datetime.fromtimestamp(int(time.mktime(self.DONE_firstWeekDate))) + datetime.timedelta(
                days=dateLength + weekday - 1)

            date = startDate
            dateList = []
            dateList.append(string)
            flag = True
            while flag:
                date = date + datetime.timedelta(days=7.0)
                if date > endDate:
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
        for classInfo in self.classList:
            i = int(classInfo["classTime"] - 1)
            className = classInfo["className"] + "|" + classInfo["classroom"]
            endTime = self.classTimeList[i]["endTime"]
            startTime = self.classTimeList[i]["startTime"]
            index = 0
            for date in classInfo["date"]:
                eventString = eventString + "BEGIN:VEVENT\nCREATED:" + classInfo["CREATED"]
                eventString = eventString + "\nUID:" + classInfo["UID"][index]
                eventString = eventString + "\nDTEND;TZID=Asia/Shanghai:" + date + "T" + endTime
                eventString = eventString + "00\nTRANSP:OPAQUE\nX-APPLE-TRAVEL-ADVISORY-BEHAVIOR:AUTOMATIC\nSUMMARY:" + className
                eventString = eventString + "\nDTSTART;TZID=Asia/Shanghai:" + date + "T" + startTime + "00"
                eventString = eventString + "\nDTSTAMP:" + self.DONE_CreatedTime
                eventString = eventString + "\nSEQUENCE:0\nBEGIN:VALARM\nX-WR-ALARMUID:" + self.DONE_ALARMUID
                eventString = eventString + "\nUID:" + self.DONE_UnitUID
                eventString = eventString + "\nTRIGGER:" + self.DONE_reminder
                eventString = eventString + "\nDESCRIPTION:事件提醒\nACTION:DISPLAY\nEND:VALARM\nEND:VEVENT\n"

                index += 1
        icsString = icsString + eventString + "END:VCALENDAR"
        # print(icsString)
        with open("school_timetable.ics", "w", encoding="utf-8") as f:
            f.write(icsString)

    def main(self):
        self.data_load()
        self.uniteSetting()
        self.classInfoHandle()
        self.icsCreateAndSave()

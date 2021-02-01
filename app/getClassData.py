import requests
from bs4 import BeautifulSoup
import re
import copy


class LoginException(Exception):
    pass


class SpiderException(Exception):
    pass


class GetClassData(object):

    def __init__(self, username, password, xnm, xqm):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.50"
        }
        self.username = username
        self.password = password
        self.xnm = xnm
        self.xqm = xqm
        self.session = self.login()

    def login(self):

        url_index = "http://ids.cumt.edu.cn/authserver/login?service=http%3A%2F%2Fmy.cumt.edu.cn%2Flogin.portal"
        url_jw_index = "http://jiaowujizhong.cumt.edu.cn:8080/jwjz/"
        url_jwxt = "http://jwxt.cumt.edu.cn/sso/jzIdsFivelogin"

        form = {
            "username": self.username,
            "password": self.password,
            "signIn": ""
        }

        session = requests.session()

        resp = session.get(url=url_index, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'lxml')
        blocks = soup.find_all(type="hidden")
        for block in blocks[:-1]:
            form[block["name"]] = block["value"]
        resp = session.post(url=url_index, headers=self.headers, data=form)
        if re.search("欢迎访问信息服务门户", resp.text):
            resp = session.get(url=url_jw_index, headers=self.headers)
            resp = session.get(url=url_jwxt, headers=self.headers)
            return session
        else:
            raise LoginException()

    def spider(self):
        # 构建url
        username = self.username
        url = "http://jwxt.cumt.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N253508&su=" + username
        # 构建form
        form = {
            "xnm": self.xnm,
            "xqm": self.xqm
        }
        # 请求
        response = self.session.post(url=url, data=form, headers=self.headers)
        data = response.json()
        if data and data["kbList"]:
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
                        for iWeek in range(startWeek, endWeek + 1, 2):
                            iclassInfo_new = copy.deepcopy(classInfo)
                            iclassInfo_new["week"] = {
                                "startWeek": str(iWeek),
                                "endWeek": str(iWeek)
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
                        for iWeek in range(startWeek, endWeek + 1, 2):
                            iclassInfo_new = copy.deepcopy(classInfo)
                            iclassInfo_new["week"] = {
                                "startWeek": iWeek,
                                "endWeek": iWeek
                            }
                            classDataList.append(iclassInfo_new)
                    else:
                        # 处理情况三：“9-11周” 正常情况
                        if len(week.split("-")) == 2:
                            # print((week.split("-")))
                            startWeek = week.split("-")[0]
                            # 利用正则，只保留str中的数字
                            cop = re.compile("\D")  # 匹配不是中文、大小写、数字的其他字符
                            startWeek = cop.sub('', startWeek)  # 将str匹配到的字符替换成空字符
                            endWeek = week.split("-")[1]
                            cop = re.compile("\D")
                            endWeek = cop.sub('', endWeek)
                            classInfo_new["week"] = {
                                "startWeek": startWeek,
                                "endWeek": endWeek
                            }
                            classDataList.append(classInfo_new)
                        # 处理情况四：“11周” 只有一周
                        elif len(week.split("-")) == 1:
                            startWeek = week.split('"')[0][:-1]
                            cop = re.compile("\D")
                            startWeek = cop.sub('', startWeek)
                            classInfo_new["week"] = {
                                "startWeek": startWeek,
                                "endWeek": startWeek
                            }
                            classDataList.append(classInfo_new)
            # print(classDataList)
            return classDataList
        else:
            # 未查到课表
            raise SpiderException

    def main(self):
        classDataList = self.spider()
        # print("爬取课表并处理成功")
        return classDataList

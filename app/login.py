import os

import requests
import execjs
from bs4 import BeautifulSoup


def get_token(pwd, salt):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # print(path)
    Passwd = execjs.compile(open(path + r'\app\aes.js').read()).call('encryptPassword', pwd, salt)
    # Passwd = execjs.compile(open(r'.\aes.js').read()).call('encryptPassword', pwd, salt)
    return Passwd


def login(username, password):
    session = requests.session()

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 FireFox / 29.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    url_login = 'http://authserver.cumt.edu.cn/authserver/login'
    url_post = 'http://authserver.cumt.edu.cn/authserver/login'

    r = session.get(url=url_login, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    salt = soup.find('input', id='pwdEncryptSalt')['value']
    execution = soup.find('input', id='execution')['value']
    # 密码加密
    salt_pwd = get_token(password, salt)

    form_login = {
        'username': username,
        'password': salt_pwd,
        '_eventId': 'submit',
        'cllt': 'userNameLogin',
        'execution': execution
    }
    rs = session.post(url=url_post, data=form_login, headers=headers, allow_redirects=False)

    if rs.status_code == 302:
        # print(rs.status_code)
        url = 'http://jwxt.cumt.edu.cn/sso/jziotlogin'
        response = session.get(url=url, headers=headers)
        # print(response.text)
        # print(response.status_code)
        return session

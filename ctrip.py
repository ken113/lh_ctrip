# encoding = utf-8

from selenium import webdriver
from selenium.webdriver import ActionChains
from time import sleep
import requests
import json

try:
    import http.cookiejar as cookielib
except Exception as e:
    print("兼容Py2.x", e)
    import cookielib  # 兼容Py2.x

class CtripAccount(object):

    def __init__(self):
        self.brower = webdriver.Chrome(executable_path='D:/selenium/chromedriver.exe')
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename='ctrip_cookie.txt')
        self.headers = {
            'Referer': 'http://vbooking.ctrip.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        }
        # 加载cookie
        self.load_cookies()  # 加载失败主动抛出异常

    def load_cookies(self):
        try:
            self.session.cookies.load(ignore_discard=True)
            return True
        except Exception as e:
            print("ctrip_cookie未能加载", e)
            print("正在重新登录...")
            # 第一次尝试登录：
            if self.login():
                print("cookie成功加载")
                return True
            else:
                print("加载cookie失败")
                return False

    def login(self, username='', password=''):
        username = '***'
        password = '***'
        self.brower.get('http://vbooking.ctrip.com/ivbk/accounts/login')

        try:
            self.brower.find_element_by_xpath('//*[@id="loginpanel_container"]/div[1]/div[1]/form/dl[1]/dd/input').send_keys(username)
            sleep(2)
            self.brower.find_element_by_xpath('//*[@id="loginpanel_container"]/div[1]/div[1]/form/dl[2]/dd/input').send_keys(password)
            self.brower.execute_script('Object.defineProperties(navigator,{webdriver:{get:() => false}});')
            status = self.brower.execute_script('window.navigator.webdriver')
            sleep(2)
            button = self.brower.find_element_by_xpath('//*[@id="verification-code"]/div[1]/div[2]')
            action = ActionChains(self.brower)
            action.click_and_hold(button).perform()  # perform()用来执行ActionChains中存储的行为
            action.reset_actions()
            action.move_by_offset(140, 0).perform()
            sleep(0.2)
            action.move_by_offset(140, 0).perform()

            self.brower.find_element_by_xpath('//*[@id="loginpanel_container"]/div[1]/div[1]/form/button').click()
            sleep(1)
            # 登录逻辑中保存session
            for cookie in self.brower.get_cookies():
                self.session.cookies.set_cookie(
                    cookielib.Cookie(version=0, name=cookie['name'], value=cookie['value'],
                                     port='80', port_specified=False, domain=cookie['domain'],
                                     domain_specified=True, domain_initial_dot=False,
                                     path=cookie['path'], path_specified=True,
                                     secure=cookie['secure'], rest={},

                                     expires=cookie['expiry'] if "expiry" in cookie else None,
                                     discard=False, comment=None, comment_url=None, rfc2109=False))

            self.session.cookies.save()
            return True
        except Exception as e:
            print("登录失败", e)
            return False

    def check_login(self):
        # 通过设置页面返回状态码来判断是否为登录状态
        inbox_url = 'https://online.ctrip.com/restapi/soa2/13953/getCurrentUserInfoV2.json'
        response = self.session.get(inbox_url, headers=self.headers, allow_redirects=False)
        status = True
        if not response.status_code == 200:
            # 第二次尝试登录：
            # print("正在重新登录...")
            if not self.login():
                status = False

        # 关闭浏览器：
        self.brower.quit()
        self.session.close()

        if status:
            return True
        else:
            return False

    def getData(self):

        url = 'https://vbooking.ctrip.com/order/orderDetail?orderId=10984408301'
        self.brower.get(url)
        self.brower.implicitly_wait(10)
        orderName = self.brower.find_element_by_xpath('//*[@id="root"]/div/div/div/div[1]/div[2]/div[2]/div[1]/div/div[2]/div[2]/a').text
        supName = self.brower.find_element_by_xpath('/html/body/div[1]/div/div/div/div[1]/div[2]/div[2]/div[1]/div/div[2]/div[2]/div[2]/div[1]/div/table/tbody/tr[4]/td').text
        print(orderName)
        orderdata = {'orderName':orderName,'supName':supName}
        print(orderdata.values())
        with open('ctrip.json', 'w', encoding='utf-8')as f:
            f.write(json.dumps(orderdata, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    account = CtripAccount()
    if account.login():
        account.getData()
    else:
        print('登录失败。。。。。')

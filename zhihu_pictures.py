# coding : UFT-8
import requests
import random
import time
import os
import os.path
from bs4 import BeautifulSoup
try:
    import cookielib
except:
    import http.cookiejar as cookielib
from PIL import Image

#该程序是爬取知乎美妆话题下关注人头像
#登录知乎
#报文头设置！
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
#知乎主页
HostUrl = 'http://www.zhihu.com'
FollowerUrl = 'https://www.zhihu.com/question/22390958/followers'
LoginUrl = 'https://www.zhihu.com/login/email'
timeout = random.choice(range(60, 180))
session = requests.session()

#使用cookie信息加载
session.cookies = cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie加载失败")

def isLogin():
    # 通过查看用户个人信息来判断是否已经登录
    url = "https://www.zhihu.com/settings/profile"
    login_code = session.get(url,allow_redirects=False,headers = headers).status_code
    print(login_code)
    if int(x=login_code) == 200:
        return True
    else:
        return False

#验证登录
def login(url):
    login_data = {
        '_xsrf' : get_xsrf(url),
        'password' : 'zjh418$!*',
        'remember_me' : 'true',
        'email' : '382853730@qq.com'
    }
    try:#不需要验证码登录
        repr=session.post(LoginUrl, data=login_data, headers=headers)
        print(repr)
    except:#需要验证码登录
        login_data['captcha_type'] = 'cn'
        login_data['captcha'] = get_captcha()
        repr = session.post(LoginUrl,data=login_data,headers=headers)
        print(repr)
    session.cookies.save()

#获取_xsrf
def get_xsrf(url):
    res = session.get(url,headers = headers,timeout=timeout).content
    _xsrf = BeautifulSoup(res,'html.parser').find('input',attrs={'name':'_xsrf'})['value']
    print(_xsrf)
    return _xsrf

#解析验证码
def get_captcha():
    t = str(int(time.time() * 1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
        f.close()
    # 用pillow 的 Image 显示验证码
    # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input("please input the captcha\n>")
    return captcha

#加载页面获取html内容，主要offset
def get_html(_xsrf):
    url = FollowerUrl
    res = session.get(url,headers=headers)#进入美妆话题
    pictures = get_pic(res.text)
    #download_pic(pictures)
    time.sleep(random.choice(range(2,5)))
    print(_xsrf)
    headers['X-Xsrftoken'] = _xsrf
    headers['Referer'] = url
    for x in range(20,100,20):
        form_data = {
            'start' : '0',
            'offset' : str(x),
            '_xsrf' : _xsrf
        }
        print(str(x))
        try:
            res= session.post(url,data=form_data,headers=headers)
            print(res)
        except:
            print("offset加载失败")
        else:
            content = res.text
            html = eval(content)['msg'][1]
            pictures = get_pic(html)
            download_pic(pictures)
        time.sleep(random.choice(range(1,5)))

#根据content内容提取头像
def get_pic(content):
    pictures = []
    bs4 = BeautifulSoup(content, "html.parser")
    users = bs4.find_all(class_='zm-profile-card zm-profile-section-item zg-clear no-hovercard')#查找所有关注者
    for user in users:
        temp = []
        username = user.find('a').get('title')#查找关注者姓名
        temp.append(username)
        picUrl = user.find('img').get('src')#查找用户头像url
        picUrl = picUrl.replace('\\','')
        temp.append(picUrl)
        print(temp)
        pictures.append(temp)
    return pictures

#下载头像
def download_pic(pictures):
    if not os.path.exists('pic'):
        os.makedirs('pic')
    for picture in pictures:
        try:
            r= requests.get(picture[1],headers)
        except:
            print("图片下载失败")
        else:
            filename = picture[0]+'.jpg'
            path = "pic/" + filename
            with open(path,'wb') as f:
                f.write(r.content)
        time.sleep(random.choice(range(1,3)))

if __name__ == '__main__':
    if isLogin():
        print("已经登录")
    else:
        print("重新登录")
        login(HostUrl)
    _xsrf = get_xsrf(HostUrl)
    get_html(_xsrf)
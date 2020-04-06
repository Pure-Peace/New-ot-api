# -*- coding: utf-8 -*-
'''
otsu.fun - Website Api Utils

@version: 1.1
@author: PurePeace
@time: 2019-12-26

@describe: a treasure house!!!
'''

from imp import reload
import time, datetime, os, requests
from kawaiis import hi
from hashlib import sha512, sha256
from ast import literal_eval
from bs4 import BeautifulSoup
import re


# get pp+ info from syrin.me (userKey = username OR userid)
def requestPlusPP(userKey):
    print(f'[{getTime(1)}]：正在请求pp+数据：{userKey} ...')
    start = time.time()
    try:
        resp = requests.get(f'https://syrin.me/pp+/u/{userKey}/', timeout=20, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'})
        soup = BeautifulSoup(resp.content, features='lxml')
        print(f'[{getTime(1)}]：请求成功，耗时：{time.time()-start}s')
        userTag = soup.find('figure', attrs={'class':'player-figure'}).find('figcaption').find('h2').find('a')
        osuid = re.findall(r'\d+', userTag.attrs.get('href'))[-1]
        osuname = userTag.text
        pp = soup.find('div', attrs={'class': 'performance-table'})
        t = pp.find('tr', attrs={'class': 'perform-total'}).find_all('th')
        totalPP = int(t[1].text.replace('pp', '').replace(',', ''))
        r = pp.find('tbody').find_all('td')
        s = [i.text.replace(':', '').replace(',','').replace('pp','').replace('(','').replace(')','').replace('Aim','').replace(' ','') for i in r]
        rawPP = {s[i]: int(s[i+1]) for i in range(0,len(s),2)}
        rawPP['Aim'] = rawPP['Total']
        del(rawPP['Total'])
        status, message = 1, {'totalPP': totalPP, 'rawPP': rawPP, 'osuid': osuid, 'osuname': osuname}
    except Exception as Err:
        print(f'[{getTime(1)}]：请求失败：', Err)
        status, message = -1, 'pp+数据获取失败（pp+的网站过于弱智...）'
    return {'message': message, 'status': status}


# get player info from osu! api v1
def requestPlayerInfo(userKey, keyType=None):
    print(f'[{getTime(1)}]：正在请求osu!玩家数据：{userKey} ...')
    start = time.time()
    try:
        link = f'https://osu.ppy.sh/api/get_user?k={osuApiv1Key}&u={userKey}'
        if keyType not in (None, '') and keyType in ('string', 'id'):
            link += f'&type={keyType}'
        resp = requests.get(link, timeout=12, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'})
        data = resp.json()
        print(f'[{getTime(1)}]：请求成功，耗时：{time.time()-start}s')
        if type(data) != list:
            status, message = -1, 'osu!官网数据获取失败（老板服务器挂了）'
        else:
            if len(data) == 0:
                status, message = -1, 'osu!官网数据获取错误（可能出了别的问题）'
            elif data[0].get('user_id') not in (None,''):
                data[0]['events'] = []
                del(data[0]['events'])
                status, message = 1, data[0]
    except Exception as Err:
        print(f'[{getTime(1)}]：出现错误：', Err)
        status, message = -1, 'osu!官网数据获取失败（老板服务器挂了）'
    return {'message': message, 'status': status}


# way to return utInfo, decorator
def utReturner(func):
    def wrapper(*args,**kwargs):
        resp, message, info, status = func(*args,**kwargs)
        if str(type(resp)) == "<class 'requests.models.Response'>":
            if resp.status_code == 200: status = 1
            else: status = -1
            message, info = utInfoPartner(message, info, status)
            try:
                resp = resp.json()
            except:
                resp = None
            return utInfo(message, resp, info, status)
        else:
            message, info = utInfoPartner(message, info, status)
            return utInfo(message, resp, info, status)
    return wrapper


# return statText
def statTextGetter(status):
    return statusInfo.get(status, '未知')


# get a text then output kawaii(text)
def kawaii(originText):
    checkModule('kawaiis')
    try:
        return f'{hi("kaomoji")} {originText}{hi("moodWords")}{hi("moodSigns")}'
    except Exception as err:
        print(str(err))
        return originText


# make some sense
def utInfoPartner(message, info, status):
    return f'{info if message == "" else message}', f'{info}{statTextGetter(status)}'


# make utInfo to return
def utInfo(message=None, data=None, info=None, status=None):
    return {'message': kawaii(message), 'data': data, 'status': status, 'info': info, 'time': getTime(1)}


# get now timeString or timeStamp
def getTime(needFormat=0, formatMS=True):
    if needFormat != 0:
        return datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S{r".%f" if formatMS else ""}')
    else:
        return time.time()


# timeString to timeStamp
def toTimeStamp(timeString):
    if '.' not in timeString: getMS=False
    else: getMS=True
    timeTuple = datetime.datetime.strptime(timeString, f'%Y-%m-%d %H:%M:%S{r".%f" if getMS else ""}')
    return float(f'{str(int(time.mktime(timeTuple.timetuple())))}'+(f'.{timeTuple.microsecond}' if getMS else ''))


# timeStamp to timeString
def toTimeString(timeStamp):
    if type(timeStamp) == int: getMS=False
    else: getMS=True
    timeTuple = datetime.datetime.utcfromtimestamp(timeStamp+8*3600)
    return timeTuple.strftime(f'%Y-%m-%d %H:%M:%S{r".%f" if getMS else ""}')


# check python module edit
def checkModule(name):
    global loadTime
    editTime = os.stat(f'./{name}.py').st_mtime
    if editTime > loadTime:
        print(f'reload module {name} at {getTime(1)}')
        reload(eval(name))
        loadTime = editTime


# generate docs with variable for method or class
def docsParameter(sub):
    def dec(obj):
       obj.__doc__ = sub
       return obj
    return dec


# generate a token: do sha512
def tokenGenerator(osuid, loginTime):
    plainTextByte = f'otsuToken {osuid}{loginTime}{loadTime}'.encode('utf8')
    return sha512(plainTextByte).hexdigest()


# to return sha256
def doSha256(string):
    return sha256(string.encode('utf8')).hexdigest()

    
# eval (safe) so evas
def evas(seeden):
    return literal_eval(seeden)


# check ip
def ipChecker(ip):
    reStr = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    if type(ip) == str or type(ip) == bytes:
        if re.match(reStr, ip): return ip


# print with time
def timePrinter(info, funcName='', backInfo='<not backInfo here>', replacement='***'):
    if info == None: info = '<func not info finded>'
    print(f'[{getTime(1)}.{funcName}]: {info.replace(replacement, backInfo)}')


# print func event decorator
def funcEventer(info={True:'success to execute.', False:'failed to execute.'}):
    def wrapper(func):
        def do(*argv, **kw):
            timePrinter('start trying to execute.', func.__name__)
            if argv or kw:
                ret = func(*argv, **kw)
            else:
                ret = func()
            if type(ret) == tuple and len(ret) > 2:
                raise Exception('more than two parameters returned, up to two.')
            if type(ret) == tuple and len(ret) == 2:
                backInfo = str(ret[-1])
                timePrinter(info.get(ret[0]), func.__name__, backInfo=backInfo)
                return ret[0]
            else:
                timePrinter(info.get(ret), func.__name__)
                return ret
        return do
    return wrapper


# cost calculate (rawPP = user pp+ info dict, type(formula) = string)
def costCalculator(rawPP, formula, osuid=''):
    keyword, message = 0, '您提交的公式无法通过自动化系统测试哦，不行不行'
    items = {
        'Aim': 3600,
        'Jump': 3000,
        'Flow': 1000,
        'Precision': 900,
        'Speed': 2000,
        'Stamina': 1800,
        'Accuracy': 2200,
        'Sum': 14500,
        'Average': 2000
    }
    if rawPP == 'test': rawPP = items
    try:
        for i in items.keys():
            temp = formula
            formula = formula.replace(i, str(rawPP.get(i)))
            if formula != temp: keyword += 1
        if keyword == 0:
            message = '您提交的公式没有用到任何一项pp+数据哦，不行不行'
            raise Exception(f'[{getTime(1)}]: {osuid}提交了不合法公式：[{formula}]')
        if len(re.findall(r'[A-Za-z]', formula)) > 0:
            message = '系统在计算时检测到pp+数据关键字以外的非法字母，此问题也可能由于您提供的玩家数据不完整而导致'
            raise Exception(f'[{getTime(1)}]: {osuid}提交了不合法公式：[{formula}]')
        status, message = 1, eval(deleteAlphabet(formula.replace('^', '**')))
        if type(message) not in (int, float):
            message = '您提交的公式无法通过自动化系统测试哦，不行不行'
            raise Exception(f'[{getTime(1)}]: {osuid}提交了不合法公式：[{formula}]')
    except Exception as Err:
        print(Err)
        status = -1
    return {'message': message, 'status': status}


# make request record info
def makeRequestInfo(request):
    return {
        'remote_addr': request.remote_addr,
        'x_forwarded_for': ipChecker(request.headers.get('X-Forwarded-For')),
        'x-real-ip': ipChecker(request.headers.get('X-Real-IP')),
        'system': request.headers.get('system_info'),
        'request': {
            'environ': request.environ,
            'url': request.url
        }
    }


# delete alphabet
def deleteAlphabet(string):
    return re.sub('[a-zA-Z]','', string)


# make authorize info
def makeAuthorizeInfo(request):
    otsuToken, osuid = request.headers.get('X-Otsutoken'), request.headers.get('osuid')
    if otsuToken == None or osuid == None: status = -1
    else: status = 1
    return {'otsuToken': otsuToken, 'osuid': osuid, 'path': request.path.strip('/')}, status


# username password checker
def registerChecker(username, password):
    username = username.strip(' ')
    password = password.strip(' ')
    if len(username) < 3 or len(username) > 12: 
        return '用户名长度必须在3-12位之间', -1
    if re.match(r'^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).{8,24}', password) == None: 
        return '密码必须含有至少一个大写字母，一个小写字母和一个数字，且长度必须在8-24位之间.', -1
    notAllow = r"~!@#$%^&*()-+=`':;{}<>?,./！·￥……（\\）；：。，、？“”【】‘’"
    for i in username:
        if i in notAllow or i == r'\n' or i == r'\\': return '用户名中检测到非法字符', -1
    return {'username':username, 'password':password}, 1


# record serve start time
loadTime = getTime()

# osu! api v1 key
osuApiv1Key = r'f73b81249384f7aec95e00aa2e906f9a094ed0d4'

# status code dict
statusInfo = { 1: '成功', 0: '默认', -1: '失败'}

# time config
timeZone = 8

# run? not.
if __name__ == '__main__':
    print('wow, you find a treasure house!!! so it dosent work')

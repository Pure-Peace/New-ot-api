# -*- coding: utf-8 -*-
'''
otsu.fun - Website Api Core

@version: 1.4
@author: PurePeace
@time: 2019-12-26

@describe: core is heart!!! (like utils)
'''

import utils
import requests
import database
import re


# request token by code
@utils.utReturner
def getOsuUserToken(osuUserAuthCode, info='获取osu!用户授权令牌', message='', status=0):
    headers = {'Content-Type': formType}
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': osuUserAuthCode,
        'redirect_uri': redirect_uri
    }
    resp = requests.post('https://osu.ppy.sh/oauth/token', data=data, headers=headers)
    return resp, message, info, status


# login by osu! authorization link
@utils.utReturner
def handleLoginByOsuAuth(osuOauthData, info='用osu!官方授权链接登录otsu!', message='', status=0, requestInfo=None):
    headers = {'Content-Type': jsonType, 'Authorization': f'Bearer {osuOauthData.get("access_token")}'}
    resp = requests.get('https://osu.ppy.sh/api/v2/me/osu', headers=headers)
    if resp.status_code == 200:
        osuUserData = resp.json()
        osuid = osuUserData.get('id')
        osuname = osuUserData.get('username')
        # try to register or login
        message, status, authorization = osuSignManager(osuid, osuname, osuOauthData, osuUserData, requestInfo)
        # success
        if status == 1:
            user = database.getUserByosuid(osuid)
            data = {
                'userInfo': {
                    'username': user.username,
                    'osuid': user.osuid,
                    'osuname': user.osuname,
                    'group': utils.evas(user.group),
                    'status': utils.evas(user.status),
                    'banned': user.banned,
                    'credit': user.credit,
                    'reg_time': str(user.reg_time),
                },
                'authorization': authorization
            }
    return data, message, info, status


def handleGetPlayerOsuid(username, osuid=None):
    try:
        resp = requests.head(f'https://osu.ppy.sh/users/{username}')
        if resp.status_code == 302:
            osuid = int(re.sub(r'\D', '', resp.next.url))
    except:
        print('xxd')
    return osuid


# verify user authorization information
def authorizeGuard(needGroup=[]):
    '''
    调用此修饰器的函数须添加参数privilege={}
    '''
    def wrapper(func):
        def haha(*args, **kw):
            authorize = kw.pop('authorization')
            cust = authorize.get('customInfo')
            message, status, privilege = authorizer(
                authorize.get('osuid'),
                authorize.get('otsuToken'),
                authorize.get('path'),
                needGroup,
                cust if cust!=None else {}
            )
            if status == 1:
                kw['privilege'] = privilege
                ret = func(*args,**kw)
                return ret
            else:
                return None, message, message, -1
        return haha
    return wrapper


# token checker decorator
def authorizer(osuid, otsuToken, path, needGroup=[], customInfo={}):
    def infoer(infoType):
        default = {'invalid':'请求被拒绝，授权认证', 'group':'请求被拒绝，认证用户组权限不足','success':'请求已确认，授权认证'}
        cust = customInfo.get(infoType)
        if cust != None and cust != '': info = cust
        else: info = default.get(infoType)
        return info

    authorize, actionTime = database.getRedisData(osuid, 'userToken', doEval=True), utils.getTime(1)
    if authorize == None or authorize.get('otsuToken') != otsuToken:
        return infoer('invalid'), -1, {}
    groupStatus, privilege = userGroupChecker(needGroup, eval(authorize.get('group')), path)
    if groupStatus != True:
        return infoer('group'), -1, {}
    if authorize.get('otsuToken') == otsuToken:
        # pass and refresh token
        database.setUserOtsuToken(osuid, otsuToken, actionTime, expiresIn, user=None)
        privilege['osuid'] = osuid
        userObject = database.getUserByosuid(osuid)
        if userObject != None: privilege['osuname'] = userObject.osuname
        else: privilege['osuname'] = '未知'
        return infoer('success'), 1, privilege


# user group checker
def userGroupChecker(needGroup, userGroup, path):
    dbSource = database.getAllDataFromTable('UserGroupPermissions')
    sourceData = {
        i.group_name: {'privilege_level': i.privilege_level, 'cant_use_api': i.cant_use_api } for i in dbSource
    }
    cantUse = [sourceData.get(d).get('cant_use_api') for d in userGroup if sourceData.get(d).get('cant_use_api') != None]
    userLevel = groupLevelGetter(sourceData, userGroup)
    needLevel = groupLevelGetter(sourceData, needGroup)
    privilege = {'userLevel': userLevel, 'userGroup': userGroup, 'cantUse': cantUse}
    if userLevel < needLevel:
        return False, privilege
    if path in cantUse:
        return False, privilege
    return True, privilege


# set user group and refresh token
@utils.utReturner
@authorizeGuard(needGroup=['otsu!admin'])
def handleSetUserGroup(data, info='修改用户所属权限组', message='', status=-1, privilege={}):
    count = 0
    try:
        user, group, actor = data.get('targetUsers'), data.get('targetGroup'), data.get('Osuid')
        if type(user) == list:
            for uid in user:
                if database.setUserGroup(uid, group, actor) == True:
                    count += 1
                loginTime = utils.getTime(needFormat=1)
                otsuToken = utils.tokenGenerator(uid, loginTime)
                database.setUserOtsuToken(uid, otsuToken, loginTime, expiresIn)
        else:
            if database.setUserGroup(user, group, actor) == True:
                count += 1
            loginTime = utils.getTime(needFormat=1)
            otsuToken = utils.tokenGenerator(user, loginTime)
            database.setUserOtsuToken(user, otsuToken, loginTime, expiresIn)
    except Exception as Err:
        print(str(Err))
    if count > 0: status = 1
    return None, f'修改了{count}位用户所属的权限组', info, status


# get osu! player data
@utils.utReturner
def handleGetPlayerDataV1(data, info='获取osu!玩家信息', message='', status=-1):
    playerKey = data.get('playerKey')
    action = data.get('action')
    kt = data.get('keyType')
    data = {}
    if playerKey not in (None,''):
        if database.getRedisData(f'{playerKey.lower()}apiV1Record', 'recordTimer') == None:
            res = getPlayerInfoWithApiv1(playerKey, keyType=kt)
            if res.get('status') != -1:
                database.setDataToRedis(f'{playerKey.lower()}apiV1Record', f'冷却中：{utils.getTime(1)}', 'recordTimer', expireS=dataRecordTimer)
        
        res = database.getPlayerApiV1Record(playerKey)
        if res != None:
            if type(res) == list:
                if len(res) > 1:
                    repairDuplicateDataRecord(res)
                    osuInfo = getPlayerInfoWithApiv1(playerKey, keyType=kt)
                    if osuInfo.get('status') != -1:
                        osuid = osuInfo.get('message').get('user_id')
                        data, status = [i.getDict for i in res if i.osuid == osuid][0], 1
                    else:
                        data, status = [i.getDict for i in res], 1
                elif len(res) == 1:
                    data, status = res[0].getDict, 1
            else:
                data, status = res.getDict, 1

    if status == 1:
        if action == 'simple':
            data = {
                'osuid': data.get('osuid'), 
                'osuname': data.get('osuname'), 
                'pp': data.get('current', {}).get('pp_raw'), 
                'rank': data.get('current', {}).get('pp_rank'),
                'country': data.get('current', {}).get('country')
            }
        if action == 'noHistory':
            data['history'] = []

    return data, message, info, status


@utils.utReturner
# get player pp+ data
def handleGetPlayerPlusPP(data, info='获取玩家pp+记录', message='', status=-1):
    playerKey, action = data.get('playerKey'), data.get('action')
    kt = data.get('keyType')
    data = {}
    if playerKey not in (None,''):
        if action == 'refresh':
            keyBackup = playerKey
            if database.getRedisData(f'{playerKey.lower()}plusPPrecord', 'recordTimer') == None:
                plusRes = utils.requestPlusPP(playerKey)
                if plusRes.get('status') == 1:
                    plusInfo = plusRes.get('message')
                    playerKey = plusInfo.get('osuid')
                    database.savePlayerPlusPPInfo(plusInfo)
                    database.setDataToRedis(f'{keyBackup.lower()}plusPPrecord', f'冷却中：{utils.getTime(1)}', 'recordTimer', expireS=dataRecordTimer)

        res = database.getPlayerPlusPPRecord(playerKey)
        if res != None:
            if type(res) == list:
                if len(res) > 1:
                    repairDuplicateDataRecord(res)
                    osuInfo = getPlayerInfoWithApiv1(playerKey, keyType=kt)
                    if osuInfo.get('status') != -1:
                        osuid = osuInfo.get('message').get('user_id')
                        data, status = [i.getDict for i in res if i.osuid == osuid][0], 1
                    else:
                        data, status = [i.getDict for i in res], 1
                elif len(res) == 1:
                    data, status = res[0].getDict, 1
            else:
                data, status = res.getDict, 1
    if status == -1: message = '如果失败了很有可能是因为没找到信息，请将action设为"refresh"进行数据更新'
    return data, message, info, status


@utils.utReturner
# get player cost info
def handleCostCalculate(data, info='获取玩家cost信息', message='', status=0):
    f1, f2 = data.get('formulaKey'), data.get('formulaContent')
    u1, u2 = data.get('userKey'), data.get('userPlusPPData')
    if f2 not in (None,''):
        return costCalculatePartner(f2, u1, u2, info, message='尝试通过自定义公式计算cost')
    elif f1 not in (None,''):
        f2 = database.getFormulaByKey(f1)
        if f2 not in (None,''):
            return costCalculatePartner(f2.content, u1, u2, info, message='尝试通过已验证的公式计算cost')
    return None, '未能找到您所指定的公式哦', info, -1


# submit your cost formula
@utils.utReturner
@authorizeGuard(needGroup=['otsu!trustedUser'])
def handleSubmitCostFormula(data, info='提交cost公式', message='', status=0, privilege={}):
    if len(data.get('content').replace(' ','')) < 5 or len(data.get('name').replace(' ','')) < 2:
        message, status = '公式内容或名称信息长度不足', -1
    if len(data.get('version').replace(' ','')) == 0:
        message, status = '公式版本信息缺失', -1
    if status != -1:
        formula = data.get('content').replace(' ', '').replace("'", '').replace('"', '')
        res = utils.costCalculator('test', formula, data.get('Osuid'))
        if res.get('status') == 1:
            userLevel = privilege.get('userLevel')
            if userLevel != None and userLevel >= 30:
                message, valid = '您的公式已经通过审核，即刻生效', 1
            else:
                message, valid = '您的公式已经提交，请等待平台人员通过审核', 0
            data['content'] = formula
            status = database.setCostFormula(data, valid)
            if status == 2:
                message, status = '请支持原创，您正在提交的公式已经有人提交过了', -1
            elif status == 3:
                message, status = '全称（公式名+版本号）出现了重复哦，请更换一个', -1
        else:
            message, status = res.get('message'), -1
    return None, message, info, status


# check login status
@utils.utReturner
@authorizeGuard(needGroup=['otsu!user'])
def handleLoginChecker(reqInfo, info='登录验证', message='', status=0, privilege={}):
    return {'osuid': privilege.get('osuid'),
            'osuname': privilege.get('osuname'),
            'cantUse': privilege.get('cantUse'),
            'tokenTime': utils.getTime(),
            'userGroup': privilege.get('userGroup'),
            'userLevel': privilege.get('userLevel')}, '登录信息已确认', info, 1


# get *LOGINED* formulas
@utils.utReturner
@authorizeGuard(needGroup=['otsu!user'])
def getFormulasLogined(info='获取公式列表（已登录）', message='', status=0, privilege={}):
    userLevel = privilege.get('userLevel')
    if userLevel != None and userLevel >= 80:
        my = [i.getDict for i in database.getAllDataFromTable('CostFormulas') if i.creator_id == privilege.get('osuid')]
        public = [i.getDict for i in database.getAllDataFromTable('CostFormulas')]
        data = {'public': public, 'my': my}
    else:
        my = [i.getDict for i in database.getAllDataFromTable('CostFormulas') if i.creator_id == privilege.get('osuid')]
        public = [i.getDict for i in database.getValidFormulas() if i.public == 1]
        data = {'public': public, 'my': my}
    return data, message, info, 1


# get *PUBLIC* formulas
@utils.utReturner
def getPublicFormulas(info='获取公式列表（未登录）', message='', status=0):
    data = {'public': [i.getDict for i in database.getValidFormulas() if i.public == 1], 'my': []}
    return data, message, info, 1


# initial and set otsu login account
@utils.utReturner
@authorizeGuard(needGroup=['otsu!user'])
def handleSetAccount(data, info='设置otsu!登录用户名和密码', message='', status=0, privilege={}):
    osuid, username, password = data.get('Osuid'), data.get('username'), data.get('password')
    # confirm whether the form information is complete
    message, status = utils.registerChecker(username, password)
    if status == 1: 
        res = database.setUserLoginAccount(osuid, message.get('username'), message.get('password'))
        reData = {'osuid': osuid}
        if res == 1: 
            rs = '您的用户信息已初始化完毕'
            reData['username'] = message.get('username')
        elif res == 2:
            rs = '您已经初始化过用户信息，本次只修改密码，用户名不会改变'
        elif res == 3:
            rs, status = '您的用户名与其它用户重复了，请更换其它用户名吧~', -1
        else:
            rs, status = '出现了未知错误...', -1
        return reData, rs, info, status
    return {'osuid': osuid}, message, info, -1


# get osu! player info with api v1
def getPlayerInfoWithApiv1(userKey, saveInfo=True, keyType=None):
    osuRes = utils.requestPlayerInfo(userKey, keyType)
    status = osuRes.get('status')
    message = osuRes.get('message')
    if status != -1 and saveInfo == True:
        database.saveApiv1PlayerInfo(message)
    return {'message': message, 'status': status}


# costCalulator section
def getRawPPFromDB(userKey):
    plusRecord, target = database.getPlayerPlusPPRecord(userKey), -1
    rawPP = {}
    osuid = None
    osuname = None
    if plusRecord != None:
        if type(plusRecord) == list:
            if len(plusRecord) > 1:
                status = -1
                repairDuplicateDataRecord(plusRecord)
            elif len(plusRecord) == 1:
                target, status = plusRecord[0], 1
            else:
                status = -1
        else: target, status = plusRecord, 1
    if target != -1:
        timer = utils.getTime() - utils.toTimeStamp(str(target.update_time))
        if timer < 1600:
            rawPP, status = eval(target.current_raw), 1
            osuid = target.osuid
            osuname = target.osuname
        else: status = -1
    else: status = -1
    return {'rawPP': rawPP, 'status': status, 'osuid': osuid, 'osuname': osuname}


# repair duplicate name in pp+ data record or api v1 data record
def repairDuplicateDataRecord(recordList):
    print('正在修复重名用户...')
    for item in recordList:
        res = utils.requestPlayerInfo(item.osuid)
        if res.get('status') != -1:
            database.saveApiv1PlayerInfo(res.get('message'))
            database.setDataRecordPlayerName(item, res.get('message').get('username'))


# costCalulator section
def costCalculatePartner(forluma, userKey, rawPP, info, message):
    res = utils.costCalculator('test', forluma)
    if res.get('status') == -1:
        return None, res.get('message'), info, -1
    else:
        if rawPP not in (None, '', {}):
             # calculate!!
            res = utils.costCalculator(rawPP, forluma)
            if res.get('status') == -1:
                return None, res.get('message'), info, -1
            else:
                return {'cost': res.get('message'), 'remark': '通过您手动提供的玩家PP+信息计算，仅供参考', 'plusPP': rawPP, 'osuid': None, 'osuname': None}, message, info, 1
        elif userKey not in (None, ''):
            res = getRawPPFromDB(userKey)
            if res.get('status') == 1:
                # calculate!!
                rawPP = res.get('rawPP')
                osuid = res.get('osuid')
                osuname = res.get('osuname')
                res = utils.costCalculator(rawPP, forluma)
                return {'cost': res.get('message'), 'remark': '30分钟内不会对同一玩家的信息进行刷新，故计算结果暂时不变', 'plusPP': rawPP, 'osuid': osuid, 'osuname': osuname}, message, info, res.get('status')
            else:
                plusRes = utils.requestPlusPP(userKey)
                plusInfo = plusRes.get('message')
                if plusRes.get('status') == 1:
                    # calculate!!
                    rawPP = plusInfo.get('rawPP')
                    osuid = plusInfo.get('osuid')
                    osuname = plusInfo.get('osuname')
                    res = utils.costCalculator(rawPP, forluma)
                    database.savePlayerPlusPPInfo(plusInfo)
                    return {'cost': res.get('message'), 'remark': '通过即时获取的玩家信息进行计算', 'plusPP': rawPP, 'osuid': osuid, 'osuname': osuname}, message, info, res.get('status')
                else:
                    return None, plusInfo, info, -1
        else:
            return None, '您提供的数据不正确哦，无法计算cost', info, -1


# get group level
def groupLevelGetter(sourceData, targetGroup):
    level = -1
    for i in targetGroup:
        l = sourceData.get(i)
        groupLevel = l.get('privilege_level')
        if l != None and groupLevel > level: level = groupLevel
    return level


# use osu account to sign in or sign up(for authorization link login)
def osuSignManager(osuid, osuname, osuOauthData, osuUserData, requestInfo=None):
    database.osuTokenSave(osuid, osuOauthData)
    user = database.getUserByosuid(osuid)
    # user not exists? register
    if user == None:
        if database.newUser(osuid, osuname, osuUserData):
            info, status = '注册登录成功', 1
        else:
            info, status = '创建用户时失败', -1
        authorization = handleUserLogin(osuid, osuUserData, requestInfo, status, loginType=2)
        return info, status, authorization
    # exists? done
    info, status = '登录成功', 1
    database.updateUserInfo(user, osuUserData)
    authorization = handleUserLogin(osuid, osuUserData, requestInfo, status, loginType=1, user=user)
    return info, status, authorization


# login by otsu account
@utils.utReturner
def loginByAccount(data, info='用otsu!账号密码登录', message='', status=0, requestInfo=None):
    username, password = data.get('username').strip(' '), data.get('password').strip(' ')
    user = database.getUserByUsername(username)
    message, status, data = userAccountVerify(user, password)
    if status == 1:
        authorization = handleUserLogin(
            data.get('userInfo').get('osuid'),
            userInfo=data,
            loginInfo=requestInfo,
            status=status,
            loginType=0,
            user=user
        )
        data['authorization'] = authorization
    return data, message, info, status


# user login handler(for account login)
def handleUserLogin(osuid, userInfo='', loginInfo='', status=-1, loginType=0, user=None):
    loginTime = utils.getTime(needFormat=1)
    database.newLoginRecord(
        osuid,
        loginTime,
        userInfo = str(userInfo),
        loginInfo = str(loginInfo),
        loginState = status,
        loginType = loginType
    )
    if status == 1:
        otsuToken = utils.tokenGenerator(osuid, loginTime)
        database.setUserOtsuToken(osuid, otsuToken, loginTime, expiresIn, user=user)
        return {'token': otsuToken, 'timestamp': utils.toTimeStamp(loginTime), 'expires_in': expiresIn}


# data getter? get my data!!!
def dataGetter(request, needDataKeys, error='请求内容不完整', record=True, records=[], strict=True):
    '''
    Args:
        :request (request): 原请求
        :needDataKeys (list): 所需数据的key列表，方法会将每个与key相对应的数据提取，若未拿到全部所需数据将会返回错误信息
            - 特别注意：获取headers中某key的数据，在needDataKeys中对应key的首字母需大写，records同
        :error (str): 错误提示
        :record (bool): 是否进行记录，方法拦截器（methodInterceptorDo）
        :records (list): 要进行记录数据的key，一般必须在needDataKeys中
    Returns:
       提取的所需数据字典, 状态, 请求信息
    '''
    data = {k:v for d in [request.get_json(), request.headers] for k,v in d.items() if k in needDataKeys}
    if strict:
        for key in needDataKeys:
            if key not in data or data.get(key) == None: return error, -1, None
    reqInfo = utils.makeRequestInfo(request)
    if record: methodInterceptorDo(request, reqInfo, [f'{i}: {data.get(i)}' for i in records])
    return data, 1, reqInfo


# verify otsu user account(for account login)
def userAccountVerify(user, password, data=None):
    if user == None:
        message, status = '请先otsu!注册账号并设置otsu!的用户名和密码', -1
    elif utils.doSha256(password) == user.password:
        message, status = '验证通过', 1
        data = {
            'userInfo': {
                'username': user.username,
                'osuid': user.osuid,
                'osuname': user.osuname,
                'group': utils.evas(user.group),
                'status': utils.evas(user.status),
                'banned': user.banned,
                'credit': user.credit,
                'reg_time': str(user.reg_time),
            }
        }
    else:
        message, status = '密码错误了，验证失败', -1
    return message, status, data


# interceptor do(global)
def interceptorDo(ipAdress, rdbname='allApiRecord', banTime=300, criticalCount=70, cacheCycleS=5, apiName='*'):
    '''
    全局拦截器做什么（目前主要防水防火）
    Args:
        ipAdress (str): 客户机ip地址.
        rdbname (str): redis数据库[变量名]
        banTime (int): 封禁时长(s)
        criticalCount (int): 连续请求达到这个次数就封禁ip
        cacheCycleS (int): 几秒钟清除一次该ip的请求次数
        apiName (str): 用来决定封禁的接口路径，如"*"表示全域封禁（该api全站），用具体api名称可以实现对某某ip使用某某接口的封禁
    '''
    ipCount = database.getRedisData(ipAdress, 'ipRecord')
    requestCount = database.getRedisData(ipAdress, rdbname)
    # only record ip++
    if ipCount == None: database.setDataToRedis(ipAdress, 1, 'ipRecord')
    else: database.setDataToRedis(ipAdress, int(ipCount) + 1, 'ipRecord')
    # record ip and judge ban ip
    if requestCount == None:
        database.setDataToRedis(ipAdress, 1, rdbname, expireS=cacheCycleS)
    else:
        database.setDataToRedis(ipAdress, int(requestCount) + 1, rdbname, expireS=cacheCycleS)
        if int(requestCount) >= criticalCount:
            if int(requestCount) >= criticalCount*7: banTime*=12*24*180
            elif int(requestCount) >= criticalCount*5: banTime*=12*24*90
            elif int(requestCount) >= criticalCount*3: banTime*=12*24
            elif int(requestCount) >= criticalCount*2: banTime*=12
            database.addToBlacklist(
                ipAdress,
                reason = f'over {int(requestCount)} consecutive visits but not not rest.',
                blackTime = banTime,
                banFor = apiName
            )


# working?
def getSomething(key):
    return database.getRedisData(key, 'otherSomething')


# method interceptor do(for method)
def methodInterceptorDo(request, reqInfo, *arg):
    '''
    方法拦截器做什么（基本同上，外加记录请求）
    '''
    apiName = request.path.replace('/', '')
    ipAdress = [reqInfo.get('remote_addr'), reqInfo.get('x_forwarded_for')]
    for ip in ipAdress:
        if ip != None:
            interceptorDo(ipAdress=ip, rdbname='loginApiRecord', criticalCount=60, cacheCycleS=10, apiName=apiName)
            database.addRequestRecord(ip, apiName, reqInfo.get('system'), reqInfo.get('request'), arg)


# check blacklist from redis
def checkBlacklist(ipAdress):
    '''
    封禁检查...
    '''
    blackItem = database.getRedisData(ipAdress, 'blackList', doEval=True)
    if blackItem != None:
        return blackItem


# delete from blacklist table
def deleteFromBlacklist(blackitem):
    database.deleteFromTable(blackitem)


# client config
client_id = '545'
client_secret = '6d3Gyr4oNrsotYgA8mWCRoLWa2o63kWpmT58Vo1z'
redirect_uri = 'http://otsu.fun/oauth'

# for dev
# client_id = '546'
# client_secret ='G5vg6u40hrBIIMjCsbWl4J1KKQ4egW6Wwxigf94v'
# redirect_uri = 'http://localhost/oauth'

# token expires in(7 days now)
expiresIn = 3600 * 24 * 7
dataRecordTimer = 1800

# some content type
formType = 'application/x-www-form-urlencoded'
jsonType = 'application/json'


# run? not.
if __name__ == '__main__':
    print('only core, so it doesnt work')

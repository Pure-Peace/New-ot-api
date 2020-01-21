# -*- coding: utf-8 -*-
'''
otsu.fun - Website Api Database

@version: 1.4
@author: PurePeace
@time: 2019-12-27

@describe: database do!!!
'''

import pymysql, utils
from flask_sqlalchemy import SQLAlchemy
from dbconfig import RedisConnect


# mysql
db = SQLAlchemy()

# redis
allApiRecord = RedisConnect(0)
loginApiRecord = RedisConnect(1)
blackList = RedisConnect(2)
userToken = RedisConnect(3)
ipRecord = RedisConnect(4)
otherSomething = RedisConnect(5)
recordTimer = RedisConnect(6)

# reset user token
# userToken.flushdb()

# user table
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    username = db.Column(db.String(100),unique=True)
    password = db.Column(db.Text)
    osuid = db.Column(db.String(100), primary_key=True)
    osuname = db.Column(db.String(100), unique=True)
    osu_usednames = db.Column(db.Text)
    osubadge = db.Column(db.Text)
    group = db.Column(db.Text)
    status = db.Column(db.Text)
    banned = db.Column(db.Boolean)
    credit = db.Column(db.Integer)
    badge = db.Column(db.Text)
    reg_time = db.Column(db.DateTime)
    lastlogin_time = db.Column(db.DateTime)
    osureg_time = db.Column(db.Text)
    country = db.Column(db.String(200))


    # a method to get userinfo as dict
    @property
    def getDict(self):
        return { i.name: getattr(self, i.name) for i in self.__table__.columns }


# user login record
class UserLoginRecord(db.Model):
    __tablename__ = 'user_login_record'
    __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    record_id_login = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    osu_user_info = db.Column(db.Text)
    login_info = db.Column(db.Text)
    login_state = db.Column(db.Integer)
    osuid = db.Column(db.String(100))
    login_type = db.Column(db.Integer)
    record_time = db.Column(db.DateTime)


# user v2 token record
class osuUserTokenV2(db.Model):
    __tablename__ = 'osu_user_token_v2_record'
    __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    token_v2 = db.Column(db.Text)
    osuid = db.Column(db.String(100), primary_key=True)
    record_time = db.Column(db.DateTime)


# requests guard
class RequestRecord(db.Model):
    __tablename__ = 'otsu_api_request_record'
    __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    record_id_request = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    ip = db.Column(db.String(300))
    request_api_name = db.Column(db.String(300))
    system_info = db.Column(db.Text)
    request_info = db.Column(db.Text)
    record_time = db.Column(db.DateTime)


# request blacklist
class RequestBanRecord(db.Model):
    __tablename__ = 'otsu_api_request_blacklist'
    __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    record_id_ban = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    ip = db.Column(db.String(300))
    mac = db.Column(db.Text)
    reason = db.Column(db.String(300))
    ban_for = db.Column(db.String(300))
    permanently = db.Column(db.Boolean)
    add_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)


# user group permissions
class UserGroupPermissions(db.Model):
    __tablename__ = 'user_group_permissions'
    __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    group_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    group_name = db.Column(db.String(300))
    privilege_level = db.Column(db.Integer)
    cant_use_api = db.Column(db.Text)
    add_time = db.Column(db.DateTime)


# api v1 player info record
class PlayerApiV1Record(db.Model):
    __tablename__ = 'player_api_v1_data_record'
    __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    osuid = db.Column(db.String(100), primary_key=True)
    osuname = db.Column(db.String(100))
    current = db.Column(db.Text)
    history = db.Column(db.Text)
    update_time = db.Column(db.DateTime)

    # a method to get this as dict
    @property
    def getDict(self):
        temp = { i.name: str(getattr(self, i.name)) for i in self.__table__.columns }
        for i in temp:
            if i in ('current', 'history'): temp[i] = eval(temp[i])
        return temp


# user pp+ info
class PlayerPlusPPRecord(db.Model):
    __tablename__ = 'player_plus_pp_data_record'
    __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    osuid = db.Column(db.String(100), primary_key=True)
    osuname = db.Column(db.String(100))
    current_total = db.Column(db.String(100))
    current_raw = db.Column(db.Text)
    history = db.Column(db.Text)
    update_time = db.Column(db.DateTime)


    # a method to get this as dict
    @property
    def getDict(self):
        temp = { i.name: str(getattr(self, i.name)) for i in self.__table__.columns }
        for i in temp:
            if i in ('current_total', 'current_raw', 'history'): temp[i] = eval(temp[i])
        return temp


# pp+ formulas
class CostFormulas(db.Model):
    __tablename__ = 'cost_formuals'
    __table_args__ = { 'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8' }
    formula_id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    full_name = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(100))
    nick_name = db.Column(db.String(100))
    version = db.Column(db.String(64))
    content = db.Column(db.Text)
    remark = db.Column(db.String(500))
    creator_id = db.Column(db.String(100))
    create_time = db.Column(db.DateTime)
    valid = db.Column(db.Boolean)
    public = db.Column(db.Boolean)

    # a method to get this as dict
    @property
    def getDict(self):
        return { i.name: str(getattr(self, i.name)) for i in self.__table__.columns }


@utils.funcEventer()
# get user by username
def getUserByUsername(username):
    return User.query.filter_by(username=username).first()


@utils.funcEventer()
# get otsu user by primary key(osuid)
def getUserByosuid(osuid):
    return User.query.get(osuid)


# get cost formula by content
def getFormulaByContent(content):
    return CostFormulas.query.filter_by(content=content).first()


# get cost formula if valid
def getValidFormulas():
    return CostFormulas.query.filter_by(valid=1).all()


# get cost formula by fullName
def getFormulaByFullName(fullName):
    return CostFormulas.query.filter_by(full_name=fullName).first()


# get cost formula by id
def getFormulaById(formulaId):
    return CostFormulas.query.get(formulaId)


# get formula by **KEY**
def getFormulaByKey(formulaKey):
    res = getFormulaById(formulaKey)
    if res != None: return res
    else: return getFormulaByFullName(formulaKey)


# get player pp+ record info
def getPlayerPlusPPRecord(userKey):
    res = PlayerPlusPPRecord.query.get(userKey)
    if res != None: return res
    else: return PlayerPlusPPRecord.query.filter_by(osuname=userKey).all()


# get player osu! api v1 record info
def getPlayerApiV1Record(userKey):
    res = PlayerApiV1Record.query.get(userKey)
    if res != None: return res
    else: return PlayerApiV1Record.query.filter_by(osuname=userKey).all()


@utils.funcEventer({True: 'userinfo *** has been updated'})
# update user when login with osu! auth
def updateUserInfo(user, osuUserData):
    user.osuname = osuUserData.get('username')
    user.osubadge = str(osuUserData.get('badges'))
    user.usednames = str(osuUserData.get('previous_usernames'))
    db.session.commit()
    return True, f'{user.osuid} - {user.osuname}'


@utils.funcEventer({True: 'osu_token_v2 for user *** has been saved.'})
# record osu token
def osuTokenSave(osuid, oauthData):
    osuTokenRecord = osuUserTokenV2.query.get(osuid)
    if osuTokenRecord == None:
        db.session.add(
            osuUserTokenV2(
                token_v2 = str(oauthData),
                osuid = osuid,
                record_time = utils.getTime(needFormat=1)
            )
        )
        db.session.commit()
    else:
        osuTokenRecord.token_v2 = str(oauthData)
        osuTokenRecord.record_time = utils.getTime(needFormat=1)
        db.session.commit()
    return True, osuid


@utils.funcEventer({True: 'otsu_token for user *** has been created.', False: 'can not find this user'})
# set token and login success!!!
def setUserOtsuToken(osuid, otsuToken, loginTime, expiresIn, user=None):
    if user == None:
        user = getUserByosuid(osuid)
    if user != None:
        user.lastlogin_time = loginTime
        db.session.commit()
        setDataToRedis(osuid, str({'otsuToken': otsuToken, 'group': user.group}), 'userToken', expireS=expiresIn)
        return True, user.osuid
    else:
        return False


@utils.funcEventer({True: 'new login request from *** has been recorded.'})
# record login
def newLoginRecord(osuid, loginTime, userInfo=None, loginInfo=None, loginState=None, loginType=None):
    db.session.add(
        UserLoginRecord(
            osu_user_info = userInfo,
            osuid = osuid,
            login_info = loginInfo,
            login_state = loginState,
            login_type = loginType,
            record_time = loginTime
        )
    )
    db.session.commit()
    return True, osuid


@utils.funcEventer({True: 'new user *** has been created.'})
# add user to table users
def newUser(osuid, osuname, osuUserData):
    db.session.add(
        User(
            osuid = osuid,
            osuname = osuname,
            osureg_time = osuUserData.get('join_date'),
            osu_usednames = str(osuUserData.get('previous_usernames')),
            osubadge = str(osuUserData.get('badges')),
            group = str(['otsu!user']),
            status = str(['good']),
            banned = False,
            badge = '[]',
            credit = 100,
            country = str(osuUserData.get('country')),
            reg_time = utils.getTime(needFormat=1)
        )
    )
    db.session.commit()
    return True, f'{osuid} - {osuname}'


@utils.funcEventer({True: 'new black item for ip: *** has been recorded.'})
# add to blacklist
def addToBlacklist(ipAdress, mac='', permanently=0, reason=None, blackTime=3600, banFor='*'):
    add_time = utils.getTime()
    setDataToRedis(ipAdress, str({'ban_for': banFor, 'reason': reason}), 'blackList', expireS=blackTime)
    db.session.add(
        RequestBanRecord(
            ip = ipAdress,
            mac = str([mac]),
            reason = reason,
            ban_for = banFor,
            permanently = permanently,
            add_time = utils.toTimeString(add_time),
            end_time = utils.toTimeString(add_time + blackTime)
        )
    )
    db.session.commit()
    return True, ipAdress


@utils.funcEventer({True: 'a request for api *** has been recorded.'})
# add request record to database
def addRequestRecord(ip, apiName, systemInfo, requestInfo, args):
    nowTime = utils.getTime(1)
    db.session.add(
        RequestRecord(
            ip = ip,
            request_api_name = apiName,
            system_info = systemInfo,
            request_info = str(requestInfo),
            record_time = nowTime
        )
    )
    db.session.commit()
    return True, f'{apiName}.{", ".join([str(i) for i in args])}'


@utils.funcEventer({True: '*** has been deleted.'})
# delete something from table
def deleteFromTable(item):
    db.session.delete(item)
    db.session.commit()
    return True, str(item)


@utils.funcEventer({True: 'initial user group permissions table'})
# initial user groups
def initialUserGroupPermissions():
    if UserGroupPermissions.query.count() == 0:
        for g in userGroups:
            db.session.add(
                UserGroupPermissions(
                    group_name = prefix + g,
                    privilege_level = userGroups.get(g),
                    add_time = utils.getTime(1)
                )
            )
        db.session.commit()
        return True


@utils.funcEventer({1: 'user *** has seted username and password', 2: 'user *** has seted username', 3: 'user *** duplicate with other user names'})
# set user login account
def setUserLoginAccount(osuid, username, password, status=2):
    user = getUserByosuid(osuid)
    if user != None:
        if user.username == None or user.username == '':
            duplicate = getUserByUsername(username)
            if duplicate == None:
                user.username = username
                status = 1
            else: status = 3
        user.password = utils.doSha256(password)
        db.session.commit()
        return status, osuid
    
    
@utils.funcEventer({True: 'user ***'})
# set user group
def setUserGroup(osuid, targetGroup, actor):
    group = UserGroupPermissions.query.get(targetGroup)
    if group != None:
        group = group.group_name
        user = getUserByosuid(osuid)
        if user != None:
            temp = eval(user.group)
            if group not in temp:
                temp.append(group)
                user.group = str(temp)
            db.session.commit()
            return True, f'{actor} change {osuid} to group {targetGroup}'


@utils.funcEventer({1: 'successfully submit forluma', 2: 'failed: content duplicate', 3: 'failed: full name duplicate'})
# set forluma
def setCostFormula(data, valid, nickName=None, version=None, remark=None, public=0):
    version = data.get('version').strip()
    name = data.get('name').strip()
    fullName = name + ' ' + version
    if getFormulaByContent(data.get('content')) != None:
        return 2
    if getFormulaByFullName(fullName) != None:
        return 3
    if int(data.get('public')) in (0,1): public = int(data.get('public'))
    db.session.add(
        CostFormulas(
            full_name = fullName,
            name = name,
            nick_name = data.get('nickName'),
            version = version,
            content = data.get('content'),
            remark = data.get('remark'),
            creator_id = data.get('Osuid'),
            create_time = utils.getTime(1),
            valid = valid,
            public = public
        )
    )
    db.session.commit()
    return 1


@utils.funcEventer({True: '*** api v1 info record success', False: '*** api v1 info record fail'})
# record osu player api v1 info
def saveApiv1PlayerInfo(data):
    userId = data.get('user_id')
    data['time'] = utils.getTime(1)
    userRecord = PlayerApiV1Record.query.get(userId)
    if userRecord == None:
        actionType = 'add'
        db.session.add(
            PlayerApiV1Record(
                osuid = userId,
                osuname = data.get('username'),
                current = str(data),
                history = str([]),
                update_time = utils.getTime(1)
            )
        )
    else:
        actionType = 'update'
        userRecord.osuname = data.get('username')
        userRecord.current = str(data)
        history = eval(userRecord.history)
        history.append(data)
        userRecord.history = str(history)
        userRecord.update_time = utils.getTime(1)

    db.session.commit()
    return True, f'{actionType} player {userId}'


# reset record player name
@utils.funcEventer({True: 'record *** reset name'})
def setDataRecordPlayerName(record, name):
    record.osuname = name
    db.session.commit()
    return True, name


@utils.funcEventer({True: '*** pp+ record success', False: '*** pp+ record fail'})
# record osu player pp+ info
def savePlayerPlusPPInfo(plusInfo):
    userId = plusInfo.get('osuid')
    plusInfo['time'] = utils.getTime(1)
    userRecord = PlayerPlusPPRecord.query.get(userId)
    if userRecord == None:
        actionType = 'add'
        db.session.add(
            PlayerPlusPPRecord(
                osuid = userId,
                osuname = plusInfo.get('osuname'),
                current_total = str(plusInfo.get('totalPP')),
                current_raw = str(plusInfo.get('rawPP')),
                history = str([]),
                update_time = utils.getTime(1)
            )
        )
    else:
        actionType = 'update'
        userRecord.osuname = plusInfo.get('osuname')
        userRecord.current_total = str(plusInfo.get('totalPP'))
        userRecord.current_raw = str(plusInfo.get('rawPP'))
        history = eval(userRecord.history)
        history.append(plusInfo)
        userRecord.history = str(history)
        userRecord.update_time = utils.getTime(1)

    db.session.commit()
    return True, f'{actionType} player {userId}'


# get all data from table
def getAllDataFromTable(tableClassName):
    return eval(f'{tableClassName}.query.all()')


# use key to get data from redis
def getRedisData(key, redisDB, doEval=False):
    data = eval(f'{redisDB}.get(key)')
    if type(data) == bytes: data = data.decode('utf-8')
    return utils.evas(data) if doEval == True and data != None else data


# set data to redis
def setDataToRedis(key, value, redisDB, expireS=None, expireMS=None, notKeyExistsDo=False, keyExistsDo=False):
    eval(f'{redisDB}.set(key, value, ex=expireS, px=expireMS, nx=notKeyExistsDo, xx=keyExistsDo)')
    return True


# config user group
prefix = 'otsu!'
userGroups = {
    'user': 5,
    'trustedUser': 15,
    'coreUser': 30,
    'developer': 80,
    'admin': 100
}


# run? not.
if __name__ == '__main__':
    print('only database duuu here, so it doesnt work')

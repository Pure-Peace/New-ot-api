# -*- coding: utf-8 -*-
'''
otsu.fun - Website Api Engine

@version: 1.6
@author: PurePeace
@time: 2019-12-27

@describe: run this file to serve.
'''

from flask import request
from flask_restplus import Resource, fields, Api
from initial import app
import utils, docs, core


# app config
api = Api(app, version='0.01',title='otsu.fun - Website Api',description='Made by PurePeace',)

# namespace
loginByOsuAuth = api.namespace('loginByOsuAuth', description='通过osu!官方授权链接登录（或注册）otsu!', path='/')
loginByAccount = api.namespace('loginByAccount', description='用otsu!账号直接登录otsu！必须是注册后设定好账号密码才可使用', path='/')
loginStatusChecker = api.namespace('loginStatusChecker', description='登录校验，同时获取用户组信息', path='/')

setLoginAccount = api.namespace('setLoginAccount', description='设置自己的otsu!登录账号及密码', path='/')
setUserGroup = api.namespace('setUserGroup', description='修改用户所属的权限组。最低权限要求：管理员', path='/')

costFormulaSubmit = api.namespace('costFormulaSubmit', description='提交cost计算公式。最低权限要求：可信用户', path='/')
costFormulaGet = api.namespace('costFormulaGet', description='查看cost计算公式，对登录和未登录两种情况返回不同值', path='/')
costCalculator = api.namespace('costCalculator', description='计算玩家在指定算法下的cost数据，同时返回pp+数据', path='/')

getPlusPPData = api.namespace('getPlusPPData', description='获取玩家pp+数据。可指定手动进行刷新操作（osu!api）', path='/')
getPlayerDataV1 = api.namespace('getPlayerDataV1', description='获取玩家osu!信息。自动进行刷新操作（osu!api）', path='/')

getPlayerOsuid = api.namespace('getPlayerOsuid', description='获取osuid（不稳定，非osu!api）', path='/')



# pasers
parser_token = api.parser().add_argument('X-OtsuToken', location='headers', type=str)
parser_osuid = api.parser().add_argument('osuid', location='headers', type=str)
parser_username = api.parser().add_argument('username', type=str, required=True, help='玩家用户名')
parser_playerKey = api.parser().add_argument('playerKey', required=True, help='玩家名或者玩家id')
parser_action = api.parser().add_argument('action', required=False, help='一个可选的操作参数，如noHistory：不返回历史数据；simple：简单数据')
parser_keyType = api.parser().add_argument('keyType', required=False, help='一个可选的参数，指定playKey是为osuid（填id）还是username（填string）')

# model
osuUserAuthCode = api.model('osuUserAuthCode', {
    'osuUserAuthCode': fields.String(required=True, description='osu!官方Oauth2用户授权code', example='就很长一串字符')
})
otsuAccount = api.model('otsuAccount', {
    'username': fields.String(required=True, description='otsu!用户名', example='AdMIn'),
    'password': fields.String(required=True, description='otsu!密码', example='Aa123456')
})
costFormula = api.model('costFormula', {
    'content': fields.String(required=True, description='可计算的合法公式字符串', example='(Jump/3000)^0.8 * (Flow/1500)^0.5 + (Speed/2000)^0.8 * (Stamina/2000)^0.5 + (Accuracy/2700)'),
    'name': fields.String(required=True, description='公式名', example='Prophet'),
    'nickName': fields.String(required=True, description='好听的公式别称', example='光法公式'),
    'version': fields.String(required=True, description='公式版本', example='v1'),
    'remark': fields.String(required=True, description='公式备注', example='OCL系列比赛所用cost公式。'),
    'public': fields.Integer(required=True, min=0, max=1,description='是否公开展示', example=1),
})
playerCostInfo = api.model('playerCostInfo', {
    'formulaKey': fields.String(required=True, description='公式全称（公式名+空格+版本号） 或 公式id', example='Prophet v1 或 1'),
    'formulaContent': fields.String(required=True, description='合法公式字符串', example='(Jump/3000)^0.8 * (Flow/1500)^0.5 + (Speed/2000)^0.8 * (Stamina/2000)^0.5 + (Accuracy/2700)'),
    'userKey': fields.String(required=True, description='玩家osuid或osuname', example='5084172'),
    'userPlusPPData': fields.String(required=True, description='合法的json格式玩家pp+数据', example={"Jump":4000,"Flow":3000,"Speed":3000,"Stamina":2800,"Accuracy":3000})
})
playerKey = api.model('playerKey', {
    'playerKey': fields.String(required=True, description='玩家osuid 或 玩家osuname', example='5084172 或 PurePeace'),
    'action': fields.String(description='一个可选的操作参数，如noHistory：不返回历史数据；simple：简单数据', example='noHistory'),
    'keyType': fields.String(description='一个可选的参数，指定playKey是为osuid（填id）还是username（填string）', example='')
})
userGroupSetting = api.model('userGroupSetting', {
    'targetUsers': fields.String(required=True, description='otsu!用户id 或 装着otsu!用户id的列表（批量）', example=''),
    'targetGroup': fields.Integer(required=True, description='目标用户组id', example=''),
})


# interceptorDo
@app.before_request
def interceptor():
    if core.getSomething('dontDoAnyThings') == 'yes':
        return {'message': 'The server is currently not allowed access', 'info': 'pause service', 'status': -1}
    ipAdress = [request.remote_addr, request.headers.get('X-Real-IP'), request.headers.get('X-Forwarded-For')]
    for ip in ipAdress:
        if utils.ipChecker(ip) != None:
            blackItem = core.checkBlacklist(ip)
            if blackItem != None:
                if blackItem.get('ban_for') == '*' or blackItem.get('ban_for') == request.path.replace('/', ''):
                    return {'message': 'You are not allowed to access this now.', 'resaon': blackItem.get('reason')}
            core.interceptorDo(ip)


# api resource(s): login with osu! web
@loginByOsuAuth.route('/loginByOsuAuth')
class loginByOsuAuth(Resource):
    @loginByOsuAuth.doc(body=osuUserAuthCode)
    @utils.docsParameter(docs.loginByOsuAuth)
    def post(self):
        data, status, reqInfo = core.dataGetter(request, ['osuUserAuthCode'])
        if status == -1: return utils.utInfo(data, status=-1)

        res = core.getOsuUserToken(data.get('osuUserAuthCode'))
        if res.get('status') == 1 and res.get('data') != None:
            res = core.handleLoginByOsuAuth(res.get('data'), requestInfo=reqInfo)
        return res


# api resource(s): login with otsu! account
@loginByAccount.route('/loginByAccount')
class loginByAccount(Resource):
    @loginByAccount.doc(body=otsuAccount)
    @utils.docsParameter(docs.loginByAccount)
    def post(self):
        data, status, reqInfo = core.dataGetter(request, ['username', 'password'], record=True, records=['username'])

        if status == -1: return utils.utInfo(data, status=-1)
        return core.loginByAccount(data, requestInfo=reqInfo)


# api resource(s): edit username or password
@setLoginAccount.route('/setLoginAccount')
@setLoginAccount.expect(parser_token, parser_osuid)
class setLoginAccount(Resource):
    @setLoginAccount.doc(body=otsuAccount)
    @utils.docsParameter(docs.setLoginAccount)
    def post(self):
        authorize, status = utils.makeAuthorizeInfo(request)
        if status == -1: return utils.utInfo('授权认证参数不完整', status=-1)

        data, status, reqInfo = core.dataGetter(request, ['username', 'password', 'Osuid'], record=True, records=['Osuid', 'username'])
                
        if status == -1: return utils.utInfo(data, status=-1)
        return core.handleSetAccount(data, authorization=authorize)


# api resource(s): login status checker
@loginStatusChecker.route('/loginStatusChecker')
@loginStatusChecker.expect(parser_token, parser_osuid)
class loginStatusChecker(Resource):
    @utils.docsParameter(docs.loginStatusChecker)
    def post(self):
        authorize, status = utils.makeAuthorizeInfo(request)
        if status == -1: return utils.utInfo('授权认证参数不完整', status=-1)

        authorize['customInfo'] = {'invalid': '登录验证'}

        reqInfo = utils.makeRequestInfo(request)
        return core.handleLoginChecker(reqInfo, authorization=authorize)


# api resource(s): put your cost formula
@costFormulaSubmit.route('/costFormulaSubmit')
@costFormulaSubmit.expect(parser_token, parser_osuid)
class costFormulaSubmit(Resource):
    @costFormulaSubmit.doc(body=costFormula)
    @utils.docsParameter(docs.costFormulaSubmit)
    def post(self):
        authorize, status = utils.makeAuthorizeInfo(request)
        if status == -1: return utils.utInfo('授权认证参数不完整', status=-1)

        data, status, reqInfo = core.dataGetter(request, ['content', 'name', 'nickName', 'version', 'remark', 'public', 'Osuid'], record=True, records=['Osuid'])
                
        if status == -1: return utils.utInfo(data, status=-1)
        return core.handleSubmitCostFormula(data, authorization=authorize)


# api resource(s): get formula list
@costFormulaGet.route('/costFormulaGet')
@costFormulaGet.expect(parser_token, parser_osuid)
class costFormulaGet(Resource):
    @utils.docsParameter(docs.costFormulaGet)
    def post(self):
        authorize, status = utils.makeAuthorizeInfo(request)
        if status == -1:
            return core.getPublicFormulas()
        else:
            res = core.getFormulasLogined(authorization=authorize)
            if res.get('status') == -1:
                return core.getPublicFormulas()
            else:
                return res


# api resource(s): cost calculate
@costCalculator.route('/costCalculator')
class costCalculator(Resource):
    @costCalculator.doc(body=playerCostInfo)
    @utils.docsParameter(docs.costCalculator)
    def post(self):
        data, status, reqInfo = core.dataGetter(request, ['formulaKey', 'formulaContent', 'userKey', 'userPlusPPData'], strict=False)

        if status == -1: return utils.utInfo(data, status=-1)
        return core.handleCostCalculate(data)


# api resource(s): get player pp+ data
@getPlusPPData.route('/getPlusPPData')
class getPlusPPData(Resource):
    @getPlusPPData.doc(body=playerKey)
    @utils.docsParameter(docs.getPlusPPData)
    def post(self):
        data, status, reqInfo = core.dataGetter(request, ['playerKey', 'action', 'keyType'], strict=False)

        if status == -1: return utils.utInfo(data, status=-1)
        return core.handleGetPlayerPlusPP(data)
    @getPlayerOsuid.expect(parser_playerKey, parser_action, parser_keyType)
    def get(self):
        return core.handleGetPlayerPlusPP({
            'playerKey': request.args.get('playerKey'), 
            'action': request.args.get('action'), 
            'keyType': request.args.get('keyType')
        })


# api resource(s): set user group
@setUserGroup.route('/setUserGroup')
@setUserGroup.expect(parser_token, parser_osuid)
class setUserGroup(Resource):
    @setUserGroup.doc(body=userGroupSetting)
    @utils.docsParameter(docs.setUserGroup)
    def post(self):
        authorize, status = utils.makeAuthorizeInfo(request)
        if status == -1: return utils.utInfo('授权认证参数不完整', status=-1)

        data, status, reqInfo = core.dataGetter(request, ['targetUsers', 'targetGroup', 'Osuid'], record=True, records=['Osuid'])

        if status == -1: return utils.utInfo(data, status=-1)
        return core.handleSetUserGroup(data, authorization=authorize)
    

# api resource(s): get player osu! data
@getPlayerDataV1.route('/getPlayerDataV1')
class getPlayerDataV1(Resource):
    @getPlayerDataV1.doc(body=playerKey)
    @utils.docsParameter(docs.getPlayerDataV1)
    def post(self):
        data, status, reqInfo = core.dataGetter(request, ['playerKey', 'action', 'keyType'], strict=False)

        if status == -1: return utils.utInfo(data, status=-1)
        return core.handleGetPlayerDataV1(data)
    @getPlayerOsuid.expect(parser_playerKey, parser_action, parser_keyType)
    def get(self):
        return core.handleGetPlayerDataV1({
            'playerKey': request.args.get('playerKey'), 
            'action': request.args.get('action'), 
            'keyType': request.args.get('keyType')
        })
        


# api resource(s): get player osuid
@getPlayerOsuid.route('/getPlayerOsuid')
@getPlayerOsuid.expect(parser_username)
class getPlayerOsuid(Resource):
    #@utils.docsParameter(docs.getPlayerDataV1)
    def get(self):
        username = request.args.get('username')
        #data, status, reqInfo = core.dataGetter(request, ['username'], strict=True)
        if not username: return None
        #if status == -1: return utils.utInfo(data, status=-1)
        return core.handleGetPlayerOsuid(username)



# run? yes!
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9531)


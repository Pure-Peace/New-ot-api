# -*- coding: utf-8 -*-
'''
otsu.fun - Website Api Docs

@version: 1.5
@author: PurePeace
@time: 2019-12-27

@describe: docs store for api (swagger ui)!!!
'''

loginByOsuAuth = \
'''
通过osu!官方认证授权代码拉取用户token，传入json数据
传参：{ 就那个code }
---
 - 1、code必填，code可通过打开osu!官方授权链接获得
 - 2、code是用于认证osu账户的
 - 3、code是一次性的，成功认证后即销毁，若还需要就得重新打开osu!官方授权链接
 - 分为两种情况：
    - 注册登录：提交用户信息，未在数据表检测到此用户，则注册，注册成功将直接登录返回该用户的数据以及令牌
    - 登录：提交用户信息，在数据表中检测到此用户，则登录，登录成功后将返回该用户的数据以及令牌
```
// 成功返回示例
{
  "message": "✧(≖ ◡ ≖✿) 登录成功成功呀...",
  "data": {
    "userInfo": {
      "username": null,
      "osuid": "5084172",
      "osuname": "PurePeace",
      "group": [
        "otsu!user"
      ],
      "status": [
        "good"
      ],
      "banned": false,
      "credit": 100,
      "reg_time": "2019-12-10 00:00:00"
    },
    "authorization": {
      "token": "5f8a9a640701d8425e66759d143c460f80aa1cda3ce41654f2df07a8e0c78d25",
      "timestamp": 1575974254.588183,
      "expires_in": 604800
    }
  },
  "status": 1,
  "info": "用osu!官方授权链接登录otsu!成功",
  "time": "2019-12-10 18:37:35.074916"
}
    
// 失败返回示例
{
  "message": "(⊙﹏⊙) 获取osu!用户授权令牌惹！！",
  "data": {
    "error": "invalid_request",
    "error_description": "The request is missing a required parameter, includes an invalid parameter value, includes a parameter more than once, or is otherwise malformed.",
    "hint": "Authorization code has expired",
    "message": "The request is missing a required parameter, includes an invalid parameter value, includes a parameter more than once, or is otherwise malformed."
  },
  "status": -1,
  "info": "获取osu!用户授权令牌失败",
  "time": "2019-12-10 16:01:19.618006"
}
```
'''


loginByAccount = \
'''
通过otsu!账号登录（首先你得注册并设置otsu!登陆帐户），传入json数据
传参：{ otsu!用户名, otsu!账户密码 }
---
 - 都必填
```
// 返回成功示例
{
  "message": "ヽ(✿ﾟ▽ﾟ)ノ 验证通过呃~",
  "data": {
    "userInfo": {
      "username": "1",
      "osuid": "9351897",
      "osuname": "Pure Peace",
      "group": [
        "otsu!user"
      ],
      "status": [
        "good"
      ],
      "banned": false,
      "credit": 100,
      "reg_time": "2019-12-10 17:55:24"
    },
    "authorization": {
      "token": "baa2c3da62607ea07ca5f45983e4d67db75b16cfbaf4ae642ab94dab70354323",
      "timestamp": 1575975386.372291,
      "expires_in": 604800
    }
  },
  "status": 1,
  "info": "用otsu!账号密码登录成功",
  "time": "2019-12-10 18:56:26.842400"
}

// 失败返回示例
{
  "message": "(*/ω＼*) 密码错误了，验证失败惹！！",
  "data": null,
  "status": -1,
  "info": "用otsu!账号密码登录失败",
  "time": "2019-12-10 15:00:56.794598"
}
```
'''


setLoginAccount = \
'''
设定otsu!登陆用户名和密码（不设定就不能用otsu!账户登录，但可以使用osu!官方授权链接登录）
Headers: X-OtsuToken, osuid
---
传参：{ 要设定的otsu!用户名, 要设定的otsu!账户密码 }

 - 全都必填
```
// 返回成功示例
{
  "message": "┗( T﹏T )┛ 您的用户信息已设置完毕哇！！",
  "data": {
    "username": "otsu!用户名"
  },
  "status": 1,
  "info": "设置otsu!登录用户名和密码成功",
  "time": "2019-12-11 02:10:19.593765"
}

```
'''


loginStatusChecker = \
'''
登录状态校验，同时返回所属用户组及权限
Headers: X-OtsuToken, osuid
---
 - Headers选填
```
// 返回成功示例
{
  "message": "✧(≖ ◡ ≖✿) 登录信息已确认呀！！",
  "data": {
    "osuid": "9351897",
    "cantUse": [],
    "tokenTime": 1578424546.945506,
    "userGroup": [
      "otsu!developer",
      "otsu!admin"
    ],
    "userLevel": 100
  },
  "status": 1,
  "info": "登录验证成功",
  "time": "2020-01-08 03:15:46.945597"
}

```
'''


costFormulaSubmit = \
'''
提交你自己的cost公式（最低权限：可信用户）
Headers: X-OtsuToken, osuid
---
传参：{ content, name, nickName, version, remark, public }

 - Headers，content，name，version必填，public默认为0
 - 提交失败的条件
   - 0、用户权限不足
   - 1、公式无法计算出数值
   - 2、公式含有非法的字符
   - 3、公式内容已经存在数据库中
 - content：公式内容
 - name：公式名
 - nickName：外号/别称
 - version：版本
 - remark：备注
 - public：是否公开（0/1）
 
```
// 返回成功示例
{
  "message": "o(*≧▽≦)ツ┏━┓ 您的公式已经通过审核，即刻生效啦...",
  "data": null,
  "status": 1,
  "info": "提交cost公式成功",
  "time": "2019-12-25 22:48:00.278536"
}

```
'''


costFormulaGet = \
'''
查看cost计算公式
Headers: X-OtsuToken, osuid
---
 - Headers选填
 - 1、未登录仅可查看已公开的公式：公开且可用
 - 2、已登录可以查看已公开的和自己的公式：自己未通过审核的公式也可查看
 - 3、高权限用户可以查看所有公式：真的是全部
```
// 返回成功示例
{
  "message": "X﹏X 获取公式列表（未登录）喵。。",
  "data": [
    {
      "formula_id": "1",
      "name": "Prophet",
      "nick_name": "光法公式",
      "version": "v1",
      "content": "(Jump/3000)^0.8*(Flow/1500)^0.5+(Speed/2000)^0.8*(Stamina/2000)^0.5+(Accuracy/2700)",
      "remark": "OCL系列比赛所用cost公式。",
      "creator_id": "651307",
      "create_time": "2019-12-25 21:58:19",
      "valid": "True",
      "public": "True"
    }
  ],
  "status": 1,
  "info": "获取公式列表（未登录）成功",
  "time": "2019-12-25 22:46:46.152138"
}

```
'''


costCalculator = \
'''
计算玩家的cost数据（注：30分钟内不会对同一玩家的pp+数据进行重复请求）
传参: { formulaKey, formulaContent, userKey, userPlusPPData }
---
 - 前二必填一项，后二必填一项（分别对应[计算公式]和[玩家信息]）
 - 计算公式信息优先级：
    - 1、formulaContent：直接提供计算公式
    - 2、formulaKey：提供公式信息：公式全名（公式名+版本号）或公式id，从服务器获取计算公式
 - 玩家信息优先级：
    - 1、userPlusPPData：直接提供PP+数据，有比较严格的格式要求：{ "Jump": 123, "Speed": 123, "xxx": xxx }，关键缺失或错误都将导致计算失败
    - 2、userKey： 提供玩家信息：玩家osuid或玩家osuname，从服务器获取玩家信息
```
// 成功返回示例

{
  "message": "w(ﾟДﾟ)w 尝试通过自定义公式计算cost呢！！",
  "data": {
    "cost": 4.527878786384173,
    "remark": "通过您手动提供的玩家PP+信息计算，仅供参考",
    "plusPP": {
      "Jump": 4000,
      "Flow": 3000,
      "Speed": 3000,
      "Stamina": 2800,
      "Accuracy": 3000
    }
  },
  "status": 1,
  "info": "获取玩家cost信息成功",
  "time": "2019-12-26 22:09:43.852039"
}
'''


getPlusPPData = \
'''
获取玩家的pp+信息记录
传参: { playerKey, action }
---
 - 必填
 - playerKey：玩家osuname或osuid
 - action：为"refresh"时尝试进行刷新操作，每名玩家的冷却时间为1600s
```
// 成功返回示例

{
  "message": "(*/ω＼*) 获取玩家pp+记录呢~",
  "data": {
    "osuid": "5084172",
    "osuname": "PurePeace",
    "current_total": 7262,
    "current_raw": {
      "Total": 3592,
      "Jump": 3551,
      "Flow": 1201,
      "Precision": 874,
      "Speed": 1884,
      "Stamina": 1651,
      "Accuracy": 1852,
      "Sum": 11013,
      "Average": 1836
    },
    "history": [
      {
        "totalPP": 7262,
        "rawPP": {
          "Total": 3592,
          "Jump": 3551,
          "Flow": 1201,
          "Precision": 874,
          "Speed": 1884,
          "Stamina": 1651,
          "Accuracy": 1852,
          "Sum": 11013,
          "Average": 1836
        },
        "osuid": "5084172",
        "osuname": "PurePeace",
        "time": "2019-12-26 19:41:10.687480"
      },
      {
        "totalPP": 7262,
        "rawPP": {
          "Total": 3592,
          "Jump": 3551,
          "Flow": 1201,
          "Precision": 874,
          "Speed": 1884,
          "Stamina": 1651,
          "Accuracy": 1852,
          "Sum": 11013,
          "Average": 1836
        },
        "osuid": "5084172",
        "osuname": "PurePeace",
        "time": "2019-12-26 19:42:47.256911"
      }
    ],
    "update_time": "2019-12-26 19:42:47"
  },
  "status": 1,
  "info": "获取玩家pp+记录成功",
  "time": "2019-12-26 20:50:57.855202"
}
'''


setUserGroup = \
'''
设置用户组
Headers: X-OtsuToken, osuid
传参: { targetUsers, targetGroup }
---
 - 全部必填
 - targetUsers：otsu!用户id 或 装着otsu!用户id的列表（批量）
 - targetGroup：目标用户组id（整数）

```
// 成功返回示例


无


'''


getPlayerDataV1 = \
'''
获取玩家osu!信息，刷新冷却时间为1600s
传参: { playerKey }
---
 - 全部必填
 - playerKey：玩家osuname或osuid

```
// 成功返回示例


{
  "message": "X﹏X 获取osu!玩家信息哇！！",
  "data": {
    "osuid": "5084172",
    "osuname": "PurePeace",
    "current": {
      "user_id": "5084172",
      "username": "PurePeace",
      "join_date": "2014-10-21 15:03:23",
      "count300": "8264604",
      "count100": "577924",
      "count50": "50338",
      "playcount": "54728",
      "ranked_score": "14849686334",
      "total_score": "79923213358",
      "pp_rank": "6292",
      "level": "100.53",
      "pp_raw": "7116.48",
      "accuracy": "98.76177215576172",
      "count_rank_ss": "35",
      "count_rank_ssh": "46",
      "count_rank_s": "616",
      "count_rank_sh": "133",
      "count_rank_a": "612",
      "country": "CN",
      "total_seconds_played": "2338737",
      "pp_country_rank": "172",
      "events": [],
      "time": "2019-12-27 10:04:51.982218"
    },
    "history": [
      {
        "user_id": "5084172",
        "username": "PurePeace",
        "join_date": "2014-10-21 15:03:23",
        "count300": "8264604",
        "count100": "577924",
        "count50": "50338",
        "playcount": "54728",
        "ranked_score": "14849686334",
        "total_score": "79923213358",
        "pp_rank": "6292",
        "level": "100.53",
        "pp_raw": "7116.48",
        "accuracy": "98.76177215576172",
        "count_rank_ss": "35",
        "count_rank_ssh": "46",
        "count_rank_s": "616",
        "count_rank_sh": "133",
        "count_rank_a": "612",
        "country": "CN",
        "total_seconds_played": "2338737",
        "pp_country_rank": "172",
        "events": [],
        "time": "2019-12-27 10:04:51.982218"
      }
    ],
    "update_time": "2019-12-27 10:04:52"
  },
  "status": 1,
  "info": "获取osu!玩家信息成功",
  "time": "2019-12-27 10:04:52.173416"
}
'''


# run? not.
if __name__ == '__main__':
    print('only docs, so it doesnt work')

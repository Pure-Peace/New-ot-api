# -*- coding: utf-8 -*-
'''
otsu.fun - Website Api DBconfig

@version: 0.6
@author: PurePeace
@time: 2019-12-10

@describe: database config...
'''
import redis


# mysql config(s)
dbServer = '****'
dbCharset = '****'
dbPort = '****'
dbName = '****'
dbUser = '****'
dbPassword = '****'


# redis config(s)
rdbServer = '****'
rdbPort = 123456
rdbPassword = '****'


# import this
def MysqlConnect():
    return f'mysql+pymysql://{dbUser}:{dbPassword}@{dbServer}:{dbPort}/{dbName}?charset={dbCharset}'


# connect redis
def RedisConnect(rdbDB):
    return redis.Redis(host=rdbServer, port=rdbPort, password=rdbPassword, db=rdbDB)


# run? not.
if __name__ == '__main__':
    print('only dbconfig... so it doesnt work')

# -*- coding: utf-8 -*-
'''
萌化处理

@version: 0.02 
@author: PurePeace
@time: 2019-12-07

@describe: moemoemoe!!!
'''

from random import choice

# 颜文字!!
kaomoji = \
r'''

w(ﾟДﾟ)w
︿(￣︶￣)︿
♪(^∇^*)
(⊙﹏⊙)
(*/ω＼*)
✧(≖ ◡ ≖✿)
ヽ(*。>Д<)o゜
(✿◡‿◡)
┗( T﹏T )┛
X﹏X
=. =
o w o
o v o
ヽ(✿ﾟ▽ﾟ)ノ
o(*≧▽≦)ツ┏━┓

'''


# 语气词!!
moodWords = \
r'''

惹
啦
呀
哟
哇
呢
喵
呃
嘛

'''


# 语气符!!
moodSigns = \
r'''

！！
~
...
。。

'''


# getter~
def hi(want):
    return choice(eval(want).strip('\n').split('\n'))


if __name__ == '__main__':
    print('moemoemoe~!!')
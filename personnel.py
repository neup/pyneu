#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import cookielib
import urllib2
import urllib
import random
import shelve
import time

import db

from util import TermColors


class Visitor(object):
    def __init__(self, opener=None):
        self.opener = opener or urllib2.build_opener(urllib2.HTTPCookieProcessor())

        self.session = db.session()

    def add_staff(self, id, workplace, name, sex):
        if self.session.query(db.Staff).get(id):
            print TermColors.WARNING, 'already!', TermColors.ENDC
            return
        dp = db.get_or_create(self.session, db.Department, name=workplace)
        # dp = db.Department(name=workplace)

        staff = db.Staff(id=id, name=name, gender=sex)
        staff.department = dp

        print TermColors.OKBLUE, 'inserted!', TermColors.ENDC


        self.session.add(staff)
        self.session.commit()


    def login(self):
        login_url = "http://202.118.27.233/2003_New/file/login.asp"
        req = urllib2.Request(login_url,
                              urllib.urlencode(dict(xm="guest", passwd='')))

        resp = self.opener.open(req)

        html = resp.read().decode("gbk")
        return u'file/content.htm' in html

    def visit(self, valxm=None, valgzh=None):
        search_url = "http://202.118.27.233/2003_New/hrsearch/search.asp"


        if not valxm:
            valxm = ''
        if not valgzh:
            valgzh = ''
        #search_params = dict(xm1=val.encode('gbk'), gzh1='')
        #search_params = dict(xm1='', gzh1=val)
        search_params = dict(xm1=valxm.encode('gbk'), gzh1=valgzh)

        req = urllib2.Request(search_url, urllib.urlencode(search_params))
        resp = self.opener.open(req)

        html = resp.read().decode("gbk")

        if u'本校无此人' in html:
            print TermColors.FAIL, "not exist", TermColors.ENDC
            return

        matches = re.findall(ur'color=#000080>(.*?)</', html.split("id=fourth_view")[-1])

        for id, workplace, name, sex in zip(matches[0::4], matches[1::4], matches[2::4], matches[3::4]):
            workplace = workplace.strip()
            name = name.strip().replace(' ', '')
            print id, workplace, name, sex,
            self.add_staff(id, workplace, name, sex)



if __name__ == '__main__':
    v = Visitor()
    v.login()
    sess = db.session()

    #for c in u'曲原甄佟门聂仲郜邢阎鞠富荣有':
    #for c in u'岳易商宝惠兰':
    #for c in u'牟雨呼冷衣裴栗':
    #for c in u'佘楚栾辛翟次寇代国信籍晋朴':
    #for c in u'沙边从英班党游阚':
    #for c in u'生戢苑巴由蔺那':
    #for c in u'迟艾初邸厉延相苍欧靳鹿符初敖印修丛芦展':
    #for c in u'铁伊槐孝教':
    #for c in u'姬仝逄甘':
    # for c in u'焦容会':
    #     v.visit(valxm=c)

    start = 1
    for i in range(start, start + 5000):
        id = "%08d" % i
        print id,
        if sess.query(db.Staff).get(id):
            print TermColors.OKGREEN, "already!", TermColors.ENDC

        else:
            v.visit(valgzh=id)


    v.session.commit()

    # for c in u'罗 梁 宋 唐 许 韩 冯 邓 曹 彭 曾 蕭 田 董 袁 潘 于 蒋 蔡 余 杜 叶 程 苏 魏 吕 丁 任 沈 姚 卢 姜 崔 钟 谭 陆 汪 范 金 石 廖 贾 夏 韦 付 方 白 邹 孟 熊 秦 邱 江 尹 薛 闫 段 雷 侯 龙 史 陶 黎 贺 顾 毛 郝 龚 邵 万 钱 严 覃 武 戴 莫 孔 向 汤'.split():
    #     v.visit(c)
    #     v.session.commit()


#     for c in u'''赵 钱 孙 李 周 吴 郑 王 冯 陈 褚 卫 蒋 沈 韩 杨
# 朱 秦 尤 许 何 吕 施 张 孔 曹 严 华 金 魏 陶 姜
# 戚 谢 邹 喻 柏 水 窦 章 云 苏 潘 葛 奚 范 彭 郎
# 鲁 韦 昌 马 苗 凤 花 方 俞 任 袁 柳 酆 鲍 史 唐
# 费 廉 岑 薛 雷 贺 倪 汤 滕 殷 罗 毕 郝 邬 安 常
# 乐 于 时 傅 皮 卞 齐 康 伍 余 元 卜 顾 孟 平 黄
# 和 穆 萧 尹 姚 邵 湛 汪 祁 毛 禹 狄 米 贝 明 臧
# 计 伏 成 戴 谈 宋 茅 庞 熊 纪 舒 屈 项 祝 董 梁
# 杜 阮 蓝 闵 席 季 麻 强 贾 路 娄 危 江 童 颜 郭
# 梅 盛 林 刁 钟 徐 邱 骆 高 夏 蔡 田 樊 胡 凌 霍
# 虞 万 支 柯 昝 管 卢 莫 经 房 裘 缪 干 解 应 宗
# 丁 宣 贲 邓 郁 单 杭 洪 包 诸 左 石 崔 吉 钮 龚'''.split():
#         print c


    # v.visit(valxm=u'宁')
    # v.visit(valxm=u'关')
    # v.visit(valxm=u'庄')
    # v.visit(valxm=u'尚')
    # v.visit(valxm=u'温')
    # v.visit(valxm=u'肖')
    # v.visit(valxm=u'战')
    # v.visit(valxm=u'柴')
    # v.visit(valxm=u'井')
    # v.visit(valxm=u'满')
    # v.visit(valxm=u'礼')
    # v.visit(valxm=u'巩')
    # v.visit(valxm=u'鄂')
    # v.visit(valxm=u'宫')
    # v.visit(valxm=u'乔')
    # v.visit(valxm=u'司')
    # v.visit(valxm=u'隋')
    # v.visit(valxm=u'申')
    # v.visit(valxm=u'从')
    # v.visit(valxm=u'闻')

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



class AAO(object):
    def __init__(self, userno, passwd=None):
        self.userno = str(userno)
        self.name = None
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        # or same as userno
        self._passwd = passwd or str(userno)

        self.base_url = "http://202.118.31.197/ACTIONQUERYCLASSSCHEDULE.APPPROCESS"

    def extract_class(self, html):
        seg = html.split('select name="strIfNeedID"', 1)[0].split('select name="ClassNO"', 1)[1]

        pattern = re.compile(r'<option value="(\w+)">(.*?)</')

        classes = pattern.findall(seg)

        # 过滤成教
        classes = filter(lambda pair: len(pair[0]) < 10, classes)

        return classes

    def extract_major(self, html):

        seg = html.split('select name="ComeYear"', 1)[0].split('name="MajorNO"', 1)[1]
        pattern = re.compile(r'<option value="(\w+)">(.*?)</')

        return pattern.findall(seg)



    def get_depts(self):
        resp = self.opener.open(self.base_url)
        html = resp.read().decode("gbk")
        seg = html.split('select name="MajorNO"', 1)[0].split('select name="DeptNO"', 1)[1]
        pattern = re.compile(r'<option value="(\d+)">(.*?)</')
        depts = pattern.findall(seg)
        return depts



    def dump_page(self, dept="", major="", comyear=""):
        opener = self.opener

        query_params = dict(
            DeptNO = dept,
            MajorNO = major,
            ComeYear = comyear,
            YearTermNO = '15',
            ClassNO = '',
            strIfNeed = '',
            strIfNeedIDArray = '' )

        query_body = urllib.urlencode(query_params)
        req = urllib2.Request(self.base_url, query_body)

        resp = opener.open(req)

        html = resp.read().decode("gbk")
        return html

if __name__ == '__main__':
    sess = db.session()
    aao =  AAO('.....')
    for kd, name in aao.get_depts():
        print kd, name,
        if name in [u"研究生院", u'成人教育学院', u'网络教育学院']:
            print TermColors.OKBLUE, "ignore!", TermColors.ENDC
            continue

        page = aao.dump_page(kd)
        coll = sess.query(db.College).filter(db.College.name == name).first()
        if not coll:
            print TermColors.WARNING, "not in college db, ignore!", TermColors.ENDC
            continue
        else:
            print TermColors.OKGREEN, "found!", TermColors.ENDC

        for km, mname in aao.extract_major(page):
            mname = mname.replace(u"（", "(").replace(u"）", ")")
            print '  ', km, mname

            major = db.get_or_create(sess, db.Major,
                                     no=km,
                                     name=mname,
                                     college=coll)

            year = 2014 # or other
            cls_page = aao.dump_page(kd, km, str(year))
            all_classes = aao.extract_class(cls_page)
            if len(all_classes) == 0:
                sess.rollback()
                print TermColors.WARNING, "empty major, rollback!", TermColors.ENDC
                continue

            for kc, cname in all_classes:
                cname = cname.replace(u"（", "(").replace(u"）", ")")
                cname = re.findall('(.*?)\[(.*?)\]', cname)[0][1]
                print '      ', kc, cname
                clss = db.get_or_create(sess, db.Class,
                                        no=kc,
                                        name=cname,
                                        grade = year,
                                        major = major)

            sess.commit()
            print '       ', TermColors.OKBLUE, "commit!", TermColors.ENDC

#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import cookielib
import urllib2
import urllib
import random
import shelve
import time
from sqlalchemy import or_

import db


from util import TermColors


class LibraryV1(object):
    def __init__(self, userno, passwd=None):
        self.userno = str(userno)
        self.name = None
        self.opener = None
        # or same as userno
        self._passwd = passwd or str(userno)


    def login(self):
        opener = self.opener or urllib2.build_opener(urllib2.HTTPCookieProcessor())

        opener.open("http://202.118.8.2:8080/opac_two/").read()

        login_url = "http://202.118.8.2:8080/opac_two/include/login_app.jsp"
        login_params = dict(
            login_type='',
            barcode=self.userno,
            password=self._passwd
        )
        login_body = urllib.urlencode(login_params)

        req = urllib2.Request(login_url, login_body)
        resp = opener.open(req)
        raw =  resp.read()

        if u'查无此读者' in raw.decode('gbk'):
            return None
        if u'读者口令错误' in raw.decode('gbk') or self.userno in ['20104001', '20104002']:
            return True         # FIXME: better way to handle pass error

        if u'读者借书卡无效' in raw.decode('gbk'):
            # student has once lost the card
            self.userno = self.userno[:8] + "01"
            return self.login()

        if u'读者借书卡处于过期停借处罚状态' not in raw.decode('gbk'):
            if raw.strip() != "ok":
                print raw.decode('gbk')
                raise RuntimeError("Login Failed! (UserNo/PassWord Error)")

        # resp = opener.open("http://202.118.8.2:8080/opac_two/reader/infoList.jsp")
        resp = opener.open("http://202.118.8.2:8080/opac_two/reader/reader_set.jsp")
        raw = resp.read()
        html = raw.decode("gbk")

        self.opener = opener

        # extract info
        return self.extract_info(html)

    def extract_extra_info(self):
        resp = self.opener.open("http://202.118.8.2:8080/opac_two/reader/reader_set_duanxin.jsp")
        raw = resp.read()

        cellphone = (re.findall(r'name="mb_number".*?value="(.*?)"', raw) or [''])[0]
        print "Cellphone:", cellphone

        return cellphone

    def extract_info(self, raw):
        barcode = re.findall(ur'str_reader_barcode.*?value="(\d+)"', raw)[0]
        assert barcode == self.userno

        email = re.findall(ur'str_reader_email.*?value="(.*?)"', raw)[0]
        print "Email:", email

        ecard = re.findall(ur'str_ecard_code.*?value="([\dA-F]+)"', raw)
        if ecard:
            ecard = ecard[0]
        else:
            ecard = None
        print "Ecard:", ecard

        name = re.findall(ur'str_reader_name.*?value="(.*?)"', raw)[0]
        self.name = name
        print "Name:", name

        sex = re.findall(ur'str_reader_gender.*?value="(.*?)"', raw)[0]
        print "Sex:", sex

        # addr maybe modified
        addr = re.findall(ur'str_reader_addr.*?value="(.*?)"', raw)[0]
        translate_table = {65296: u'0', 65297: u'1', 65298: u'2', 65299: u'3',
                           65300: u'4', 65301: u'5', 65302: u'6', 65303: u'7',
                           65304: u'8', 65305: u'9'}
        addr = addr.translate(translate_table)
        print "Addr:", addr

        created_date = re.findall(ur'str_card_start_date.*?value="(.*?)"', raw)[0]

        expire_date = re.findall(ur'str_card_due_date.*?value="(.*?)"', raw)[0]

        print "Due:", created_date, "-", expire_date

        role = re.findall(ur'str_readertype.*?value="(.*?)"', raw)[0]
        print "Role:", role

        workplace = re.findall(ur'str_workplace.*?value="(.*?)"', raw)[0]
        print "Workplace:", workplace

        # fixture
        # if workplace == u"理学院" and addr.startswith(u"理"):
        #     addr = addr[1:]

        addr = normalize_class_name(name=addr, college=workplace)
        #addr = addr.replace(u"锟斤拷锟斤拷锟斤拷", u"材物")
        deposit = re.findall(ur'str_deposit.*?value="(.*?)"', raw)[0]
        print "Deposit:", deposit

        cellphone = self.extract_extra_info()

        del raw
        return locals()



def normalize_class_name(name, college):
    if name == u"管理营销1002":
        name = u"管理营销"

    if name == u"管理信息1002":
        name = u"管理信息"


    if name == u"信息自动化090":
        name == u"信息自动化"
    if name.startswith(u"软件数字"):
        name = name[2:]

    if name.startswith(u"软件信息"):
        name = name.replace(u"软件信息", u"软信")

    name = name.replace(u"社会体育", u"体育")
    if name.startswith(u"信自动化"):
        name = name[1:]

    if name.startswith(u"信计算机"):
        name = name[1:]

    if college == u"管理学院" and len(name) > 7 and name.startswith(u"工商") and u"类" not in name:
        name = name[2:]

    if college == u"管理学院" and len(name) > 7 and name.startswith(u"管理"):
        name = name[2:]


    if college == u"管理学院" and name.startswith(u"工管") and (('1' not in name) or len(name) > 7):
        name = name[2:]

    if college == u"材冶学院" and len(name) > 7 and name.startswith(u"材冶"):
        name = name[2:]

    if college == u"信息学院" and len(name) > 7 and name.startswith(u"信息"):
        name = name[2:]

    if college == u"文法学院" and len(name) > 7 and name.startswith(u"文法"):
        name = name[2:]

    if college == u"机械学院" and len(name) > 7 and name.startswith(u"机械"):
        name = name[2:]

    if college == u"艺术学院" and len(name) > 7 and name.startswith(u"艺术"):
        if name.startswith(u"艺术设计"):
            name = name.replace(u"艺术设计", u"艺术")
        else:
            name = name[2:]

    if college == u"资土学院" and len(name) > 7 and name.startswith(u"资土"):
        name = name[2:]

    if college == u"江河建筑学院" and len(name) > 7 and name.startswith(u"江河"):
        name = name[2:]

    if college == u"中荷生物医学与信息工程学院" and len(name) > 7 and name.startswith(u"中荷"):
        name = name[2:]

    if college == u"生命科学与健康学院" and len(name) > 7 and name.startswith(u"生科"):
        name = name[2:]


    name = name.replace(u"工管市销", u"营销")
    name = name.replace(u"信通信", u"通信")
    name = name.replace(u"应用物理", u"应物")
    name = name.replace(u"资源勘察工程", u"勘查")
    name = name.replace(u"工业设计", u"设计")

    name = name.replace(u"国防", u"")
    name = name.replace(u"班", u"")
    name = name.replace(u"信测控", u"测控")
    name = name.replace(u"信电科", u"电科")
    name = name.replace(u"信电气", u"电气")

    name = name.replace(u"软件工程", u"软件")
    name = name.replace(u"外语", "")
    if college == u"理学院":
        if name.startswith(u"理学院"):
            name = name[3:]
        elif name.startswith(u"理"):
            name = name[1:]

    return name


class LibraryV2(object):
    def __init__(self, userno, passwd=None):
        self.userno = str(userno)
        self.name = None
        self.opener = None
        # or same as userno
        self._passwd = passwd or str(userno)


    def login(self):
        opener = self.opener or urllib2.build_opener(urllib2.HTTPCookieProcessor())

        resp = opener.open("http://202.118.8.19/V?func=find-db-1-lcl&RN=%d" % (random.random() * 1000000000))
        raw = resp.read()

        jump_url = re.findall(r"var url = '(.*?)'", raw)[0]
        jump_url = jump_url.replace("&amp;", '&')

        resp = opener.open(jump_url)
        raw = resp.read()

        jump_url = re.findall(r"location = '/goto/(.*?)'", raw)[0]

        resp = opener.open(jump_url)
        raw = resp.read()

        login_cb_url_pattern = re.compile(r'var loginurl="(.*?)"')
        login_cb_url = login_cb_url_pattern.findall(raw)[0]


        login_params = dict(
            func="login",
            calling_system="metalib",
            term1="short",
            selfreg="",
            bor_id=self.userno,
            bor_verification=self._passwd,
            institute="NEU",
            url = login_cb_url.split('url=', 1)[-1]
        )

        login_url = "http://202.118.8.19/pds"
        login_body = urllib.urlencode(login_params)

        req = urllib2.Request(login_url, login_body)
        resp = opener.open(req)
        raw =  resp.read()

        jump_url = re.findall(r"location = '/goto/logon/(.*?)'", raw)[0]

        resp = opener.open(jump_url)
        raw = resp.read()

        name = re.findall(r'已登录用户：(.*?)"', raw)[0].decode("utf-8")

        self.name = name
        self.opener = opener



def runV2():
    db = shelve.open("./neu.db")

    print len(db)
    raise SystemExit
    # for no in xrange(20130001, 20133333):
    for no in xrange(20135000 - 100, 20136000):
        no = str(no)
        if no in db:
            print no, db[no], "√"
            continue
        try:
            t = LibraryV2(no)
            t.login()
            print t.userno, t.name
            db[t.userno] = t.name
            db.sync()
            time.sleep(0.3)
        except KeyboardInterrupt:
            print "Interrupted!"
            raise SystemExit
        except:
            print no, "......", "×"

    db.close()


def runV1():
    sess = db.Session()
    # FIXME: 20112266 软件1108? 1109
    # ============
    start = 20090000
    for no in range(start, start + 6000):
        no = str(no)
        print no,
        try:
            stu = sess.query(db.Student).filter(db.Student.no == no).first()
            if stu:
                print TermColors.OKGREEN, 'in db', TermColors.ENDC
                continue
            else:
                print TermColors.WARNING, 'not in db', TermColors.ENDC

            t = LibraryV1(no)
            info = t.login()
            if info is None:    # no user
                print TermColors.WARNING, 'not exist', TermColors.ENDC
                continue
            if info == True:
                print TermColors.FAIL, 'pass error', TermColors.ENDC
                # has user but pass error
                stu = db.Student(no=no, memo='not_yet_acquired')
                sess.add(stu)
                sess.commit()
                print TermColors.OKGREEN, "commit empty student!", TermColors.ENDC
                continue

            # print info
            stu = db.Student(no=no, name=info['name'], gender=info['sex'])
            stu_lib_acct = db.LibraryAccount(barcode=info['barcode'],
                                             password=no,
                                             expired_at=info['expire_date'],
                                             ecard=info['ecard'])

            stu_lib_acct.student = stu

            # fuck this is must
            cls = sess.query(db.Class).filter(or_(db.Class.name == info['addr'],
                                                  db.Class.alias1 == info['addr'])).first()

            if cls:
                print TermColors.OKBLUE, "got class =>", cls.name, cls.major.name, TermColors.ENDC
                stu.klass = cls
                stu.major = cls.major
                stu.college = cls.college

            else:
                print TermColors.FAIL, "class not found !!", TermColors.ENDC
                # Fixture for foreign students
                major_mapper_2011 = {
            #                 elif workplace == u"管理学院" and addr.startswith(u"工管") and barcode.startswith("2011"):
            # addr = addr[2:]
            # if addr == u"金融学":
            #     addr = u"金融1101"
            # if addr == u"工商管理":
            #     addr = u"工商1101"
                    u'机械机械工程': 259,
                    u'资土资源勘察': 252,
                    u'机械工程自动化': 259,
                    u'理学院信计': 277,
                    u'理学院应化': 280,
                    u'中荷生医': 293,
                    u'材冶冶金工程': 254,
                    u'资土土木工程': 248,
                    u'资土采矿工程': 246,
                    u'资土建筑学': 237,
                    u'信息计算机科学': 262,
                    u'工业工程': 271,
                }
                if no.startswith("2011"):
                    major_id = major_mapper_2011.get(info['addr'], None)
                    if major_id is None: #
                        coll = info['workplace'].replace(u"学院", '')
                        addr = info['addr'].replace(coll, '')
                        a_fridend_class = sess.query(db.Class).filter(db.Class.name.like(addr + "1101")).one()
                        print TermColors.WARNING, "friend class =>", a_fridend_class.name, a_fridend_class.major.name, TermColors.ENDC
                        stu.major = a_fridend_class.major
                        stu.college = stu.major.college
                    else:
                        stu.major = sess.query(db.Major).get(major_id)
                        stu.college = stu.major.college
                    print TermColors.OKBLUE, "got major =>", stu.major.name, TermColors.ENDC

                elif no.startswith("2012"):
                    coll = info['workplace'].replace(u"学院", '')
                    addr = info['addr'].replace(coll, '').replace(u"外语", "")
                    if "1" in addr: # if contains classname:
                        raise RuntimeError

                    a_fridend_class = sess.query(db.Class).filter(db.Class.name.like(addr + "1201")).first()
                    if not a_fridend_class:
                        a_fridend_class = sess.query(db.Class).join(db.Class.major).filter(db.Major.name.like('%' + addr + '%'),
                                                                                           db.Class.grade == 2012).first()

                    if a_fridend_class:
                        print TermColors.WARNING, "friend class =>", a_fridend_class.name, a_fridend_class.major.name, TermColors.ENDC
                        stu.major = a_fridend_class.major
                        stu.college = stu.major.college
                    else:
                        stu.college = stu.major.college

                elif no.startswith("2010"):
                    coll = info['workplace'].replace(u"学院", '')
                    addr = info['addr'].replace(coll, '').replace(u"外语", "")
                    if "1" in addr: # if contains classname:
                        raise RuntimeError

                    a_fridend_class = sess.query(db.Class).filter(db.Class.name.like(addr + "1001")).first()
                    if not a_fridend_class:
                        a_fridend_class = sess.query(db.Class).join(db.Class.major).filter(db.Major.name.like('%' + addr + '%'),
                                                                                           db.Class.grade == 2010).first()

                    if a_fridend_class:
                        print TermColors.WARNING, "friend class =>", a_fridend_class.name, a_fridend_class.major.name, TermColors.ENDC
                        stu.major = a_fridend_class.major
                        stu.college = stu.major.college
                    else:
                        stu.college = stu.major.college

                elif no.startswith("2013"):
                    coll = info['workplace'].replace(u"学院", '')
                    addr = info['addr'].replace(coll, '').replace(u"外语", "")
                    if "1" in addr: # if contains classname:
                        raise RuntimeError

                    print aadr
                    a_fridend_class = sess.query(db.Class).filter(db.Class.name.like(addr + "1301")).first()
                    if not a_fridend_class:
                        a_fridend_class = sess.query(db.Class).join(db.Class.major).filter(db.Major.name.like('%' + addr + '%'),
                                                                                           db.Class.grade == 2012).first()

                    if a_fridend_class:
                        print TermColors.WARNING, "friend class =>", a_fridend_class.name, a_fridend_class.major.name, TermColors.ENDC
                        stu.major = a_fridend_class.major
                        stu.college = stu.major.college
                    else:
                        stu.college = stu.major.college
                else:
                    raise SystemExit
            # raise KeyboardInterrupt


            stu.memo = "cellphone:%s|email:%s" % (info['cellphone'], info['email'])

            sess.add_all([stu, stu_lib_acct])
            sess.commit()
            print TermColors.OKGREEN, "commit!", TermColors.ENDC

        except KeyboardInterrupt:
            print "ends at", no
            raise SystemExit
        # except Exception as e:

        #     print "EEE", e
        #     continue



if __name__ == '__main__':
    #runV1()
    runV1()

#-*- coding:utf-8 -*-
import sys
import re
import urllib2, cookielib, urllib
import aao

class Score(object):
    """docstring for Score"""

    urlLogin = 'http://202.118.31.197/ACTIONLOGON.APPPROCESS'
    urlScore = 'http://202.118.31.197/ACTIONQUERYSTUDENTSCORE.APPPROCESS'
    urlCaptcha = 'http://202.118.31.197/ACTIONVALIDATERANDOMPICTURE.APPPROCESS'

    def __init__(self):
        super(Score, self).__init__()

    def _aaoLogin(self, user, password):
        cookie = cookielib.CookieJar()

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

        im = aao.get_image(opener)
        captcha = aao.guess_captcha(im)

        loginValues = {'WebUserNO': user,
                       'Password': password,
                       'Agnomen': str(captcha),
                       'submit7': '登录'}

        postContent = urllib.urlencode(loginValues)
        req = urllib2.Request(self.urlLogin, postContent)
        login = opener.open(req)
        if login.read().find("WebUserNO") == -1:
            print "login ok"
        else:
            print "login failed"
            raise SystemExit(1)
        return opener

    def getScore(self, user, password):
        opener = self._aaoLogin(user, password)
        loginValues = {'YearTermNO': 11}
        postContent = urllib.urlencode(loginValues)
        req = urllib2.Request(self.urlScore, postContent)
        scorePage = opener.open(req)
        rawText = scorePage.read().decode('gbk')
        result = self.scanClasses(rawText)
        return result

    def scanClasses(self, text):
        print text
        result = {}
        pattern = re.compile(r'''<td nowrap>\&nbsp;(?P<className>.+?)</td>''')
        classNames = re.findall(pattern, text)
        pattern = re.compile(r'''--><td align="center" nowrap>(?P<score>.+?)</td>''', re.U)
        score = re.findall(pattern, text)
        for i in xrange(0, len(classNames)):
            result[classNames[i]] = score[i]
        return result

    @staticmethod
    def queryScore(user, password):
        s = Score()
        return s.getScore(user, password)

if __name__ == '__main__':
    result = Score.queryScore("20103550", "Uriel7742")
    print str(result).encode('utf-8')

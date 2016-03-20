# -*- coding=utf-8 -*-
# Auther: Conan
# Email: 1526840124@qq.com
# Description: A tool to calculate your credit for uestc
import urllib
import urllib2
import cookielib
import lxml.html
import sys
reload(sys)
#python默认环境编码时ascii
sys.setdefaultencoding("utf-8")

# 0. set the username and password

if len(sys.argv) <3:
    print "Usage: uestc-grade.py username password"
    sys.exit()

username=sys.argv[1]
password=sys.argv[2]

# 1. create a opener with cookie
cookie = cookielib.CookieJar()
# cookie_support = urllib2.HTTPCookieProcessor(cookie)
openner = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
# openner = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
# urllib2.install_opener(openner)

# 2. get the login page with cookie
login_url = 'http://idas.uestc.edu.cn/authserver/login?service=http://portal.uestc.edu.cn/logout.portal'
uestc_login_page = openner.open(login_url).read()
# for i in cookie:
#    print i

# 3. get the post data from the login page
# xpath: //*[@id='casLoginForm']/input   get方法用于获取value属性的值
uestc_login_page_parcer = lxml.html.fromstring(uestc_login_page)
post_data_input = uestc_login_page_parcer.xpath('//*[@id="casLoginForm"]/input')
# print post_data_input[0].get('name')
# print post_data_input[0].get('value')
post_data = {}
for i in post_data_input:
    post_data[i.get('name')] = i.get('value')
# print post_data
# add the username and password

post_data['username'] = username
post_data['password'] = password
# print post_data
urlencode_post_data = urllib.urlencode(post_data)

# 4. set headers
# User-Agent	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0
user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'
headers = {'User-Agent': user_agent}

# 5. make a request to login
# http://idas.uestc.edu.cn/authserver/login?service=http://portal.uestc.edu.cn/logout.portal
post_url = 'http://idas.uestc.edu.cn/authserver/login?service=http://portal.uestc.edu.cn/logout.portal'
req = urllib2.Request(post_url, urlencode_post_data, headers)

# 6.handle the redirection
redirection_response = openner.open(req)
# for i in cookie:
#    print i
# print redirection_response.geturl()
# http://portal.uestc.edu.cn/index.portal?ticket=ST-170422-7y2u41iGFTdSJBbzRRLy1458454181068-fQRA-cas
# http://portal.uestc.edu.cn/index.portal
reidrection_url = 'http://portal.uestc.edu.cn/index.portal'
redirection_req = urllib2.Request(reidrection_url, headers=headers)
redirection_page = openner.open(redirection_req)
# print redirection_page.read()
# for i in cookie:
#    print i

# 7.open the education system
# http://eams.uestc.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR
course_url = 'http://eams.uestc.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR'
course_req = urllib2.Request(course_url, headers=headers)
course_page = openner.open(course_req).read()
# print course_page

# 8. get the course ID and calculate the grade
course_page_parcer = lxml.html.fromstring(course_page)
# xpath:.//*[@id='grid21344342991_data']/tr/td[2]
course_code_list = course_page_parcer.xpath('//*[@id="grid21344342991_data"]/tr/td[2]/text()')
course_credit_list = course_page_parcer.xpath('//*[@id="grid21344342991_data"]/tr/td[6]/text()')
# >=60 或 通过 或 A/B/C 才可计入已获学分
course_grade_list = map(lambda x: x.strip(),
                        course_page_parcer.xpath('//*[@id="grid21344342991_data"]/tr/td[7]/text()'))
# print course_code_list
# print course_credit_list

course_count = len(course_code_list)
# A:核心通识课程 B:基础通识课程 c:交叉通识课程 D:学科通识课程
# E:学科基础课程 F:学科拓展课程 G:专业核心课程 H:专业选修课程
# I:素质教育选修课程 J:创新与拓展项目 K:实验课程 L:实习实训
course_grade_count = {}
course_grade_count['A'] = 0
course_grade_count['B'] = 0
course_grade_count['C'] = 0
course_grade_count['D'] = 0
course_grade_count['E'] = 0
course_grade_count['F'] = 0
course_grade_count['G'] = 0
course_grade_count['H'] = 0
course_grade_count['I'] = 0
course_grade_count['J'] = 0
course_grade_count['K'] = 0
course_grade_count['L'] = 0

course_grade_kind={}
course_grade_kind['A'] = u'核心通识课程'
course_grade_kind['B'] = u'基础通识课程'
course_grade_kind['C'] = u'交叉通识课程'
course_grade_kind['D'] = u'学科通识课程'
course_grade_kind['E'] = u'学科基础课程'
course_grade_kind['F'] = u'学科拓展课程'
course_grade_kind['G'] = u'专业核心课程'
course_grade_kind['H'] = u'专业选修课程'
course_grade_kind['I'] = u'素质教育选修课程'
course_grade_kind['J'] = u'创新与拓展项目'
course_grade_kind['K'] = u'实验课程'
course_grade_kind['L'] = u'实习实训'

for i in range(0, course_count-1):
    if course_grade_list[i] >= 60 or course_grade_list[i] == u'通过' or course_grade_list == 'A' or course_grade_list == 'B' or course_grade_list == 'C':
        if course_code_list[i][0] in ('A','B','C','D','E','F','G','H','I','J','K','L'):
            course_grade_count[course_code_list[i][0]] = course_grade_count[course_code_list[i][0]] + float(course_credit_list[i])

for k in course_grade_count:
    print "%s %.1f" % (course_grade_kind[k],course_grade_count[k])





#!/usr/bin/env python3
import os
import time
import tornado.gen
import tornado.web
import tornado.ioloop
import tornado.options
import rethinkdb as r
import datetime

tornado.options.define('port', default=9999, type=int)

classType = {
    1: '人文社会科学类',
    2: '工程技术基础类',
    3: '体育',
}
classCampus = {
    1: '大学城校区',
    2: '东风路校区',
    3: '龙洞校区',
}
classAcademy = {
    1: '通识教育中心',
    2: '体育部',
    3: '学生处',
}


def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return time.strftime(format, time.localtime(value))


def average(num):
    if not num: return -1
    result = num[0]
    for i in num[1:]:
        result += i
    return round(result / len(num), 2)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render('index.html', location='index')


class CourseHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        commentSort = yield r.table('comments').group('CourseId').count().run(conn)
        courses = []
        coursesCur = yield r.table('courses').filter({'isPub': 1}).run(conn)
        Mark = yield r.table('comments').group('CourseId').avg('Mark').run(conn)
        while (yield coursesCur.fetch_next()):
            course = yield coursesCur.next()
            courses.append(course)
        for i in courses:
            i['Type'] = classType[i['Type']]
            i['Campus'] = classCampus[i['Campus']]
            i['Academy'] = classAcademy[i['Academy']]
            try:
                i['Mark'] = Mark[i['id']]
            except:
                i['Mark'] = -1
            try:
                i['CommentCount'] = commentSort[i['id']]
            except:
                i['CommentCount'] = 0
        return self.render('course.html', location='course', classType=classType, classCampus=classCampus,
                           classAcademy=classAcademy, courses=courses)

    @tornado.gen.coroutine
    def post(self):
        try:
            inf = {
                'Name': self.get_body_argument('Name'),
                'TeacherName': self.get_body_argument('TeacherName'),
                'Type': int(self.get_body_argument('Type')),
                'Campus': int(self.get_body_argument('Campus')),
                'Academy': int(self.get_body_argument('Academy')),
                'FinalTestType': '管理员尚未整理',
                'isPub': 0,
            }
        except:
            return self.redirect('/course?code=0')
        yield r.table('courses').insert(inf).run(conn)
        return self.redirect('/course?code=2')


class CourseDetailHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, CourseId):
        course = yield r.table('courses').get(CourseId).run(conn)
        if not course: return self.send_error(404)
        course['Type'] = classType[course['Type']]
        course['Campus'] = classCampus[course['Campus']]
        course['Academy'] = classAcademy[course['Academy']]
        course['Count'] = yield r.table('comments').filter({'CourseId': CourseId}).count().run(conn)
        Mark = []
        CheckIn = []
        course['Tags'] = []
        commentCur = yield r.table('comments').get_all(CourseId, index='CourseId').pluck(
                {'Mark', 'CheckIn', 'Tags'}).run(conn)
        while (yield commentCur.fetch_next()):
            n = yield commentCur.next()
            Mark.append(n['Mark'])
            CheckIn.append(n['CheckIn'])
            course['Tags'] += n['Tags']
        course['Mark'] = average(Mark)
        course['CheckIn'] = average(CheckIn)
        course['Tags'] = list(set(course['Tags']))
        return self.render('course.detail.html', location='course', course=course)

    @tornado.gen.coroutine
    def post(self, CourseId):
        try:
            inf = {
                'CourseId': CourseId,
                'StudentId': int(self.get_body_argument('StudentId')),
                'NickName': self.get_body_argument('NickName'),
                'Content': self.get_body_argument('Content'),
                'CheckIn': int(self.get_body_argument('CheckIn')),
                'FinalTestType': self.get_body_argument('FinalTestType'),
                'Mark': int(self.get_body_argument('Mark')),
                'Time': (yield r.now().run(conn)),
            }
        except:
            return self.redirect('/course/%s?code=0' % CourseId)
        try:
            inf['Tags'] = self.get_body_argument('Tag').split(',')
        except:
            inf['Tags'] = []
        if (yield r.table('comments').filter(
                {'StudentId': inf['StudentId'], 'CourseId': inf['CourseId'], }).count().run(
                conn)): return self.redirect(
                '/course/%s?code=-1' % CourseId)
        yield r.table('comments').insert(inf).run(conn)
        return self.redirect('/course/%s?code=1' % CourseId)


class CourseDetailPageHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, courseId, pageNum):
        comment = yield r.table('comments').filter({'CourseId': courseId}).order_by(r.desc('Time')).skip(
                (int(pageNum) - 1) * 10).limit(10).run(conn)
        for i in comment:
            i['Time'] = (i['Time'] + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
        return self.render('course.datail.page.html', location='course', comment=comment)


class AboutHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render('about.html', location='about')


@tornado.gen.coroutine
def main():
    global conn
    tornado.options.options.parse_command_line()
    r.set_loop_type('tornado')
    conn = yield r.connect(host='10.0.3.12', db='gec')
    settings = {
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    }
    application = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/course', CourseHandler),
        (r'/course/(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})', CourseDetailHandler),
        (r'/course/(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})/page/(\d+)', CourseDetailPageHandler),
        (r'/about', AboutHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
    ], **settings)
    application.listen(tornado.options.options.port, '127.0.0.1', xheaders=True)


if __name__ == '__main__':
    main()
    tornado.ioloop.IOLoop.instance().start()

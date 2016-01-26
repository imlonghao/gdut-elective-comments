#!/usr/bin/env python3
import os
import time
import tornado.gen
import tornado.web
import tornado.ioloop
from db import db
from bson.objectid import ObjectId
from tornado.options import define, options

define('port', default=9999, type=int)

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
        commentSort = []
        commentSortCur = db.comments.aggregate([{'$group': {'_id': '$CourseId', 'num': {'$sum': 1}}}])
        courses = []
        coursesCur = db.courses.find({'isPub': 1})
        while (yield commentSortCur.fetch_next):
            commentSort.append(commentSortCur.next_object())
        while (yield coursesCur.fetch_next):
            courses.append(coursesCur.next_object())
        for i in courses:
            i['Type'] = classType[i['Type']]
            i['Campus'] = classCampus[i['Campus']]
            i['Academy'] = classAcademy[i['Academy']]
            cur = db.comments.find({'CourseId': i['_id']}, {'Mark': 1})
            Mark = []
            while (yield cur.fetch_next):
                n = cur.next_object()
                Mark.append(n['Mark'])
            i['Mark'] = average(Mark)
            try:
                i['CommentCount'] = [x['num'] for x in commentSort if x['_id'] == i['_id']][0]
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
        yield db.courses.insert(inf)
        return self.redirect('/course?code=2')


class CourseDetailHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, CourseId):
        course = yield db.courses.find_one({'_id': ObjectId(CourseId), 'isPub': 1})
        if not course: return self.send_error(404)
        course['Type'] = classType[course['Type']]
        course['Campus'] = classCampus[course['Campus']]
        course['Academy'] = classAcademy[course['Academy']]
        course['Count'] = yield db.comments.find({'CourseId': ObjectId(CourseId)}).count()
        Mark = []
        CheckIn = []
        course['Tags'] = []
        commentCur = db.comments.find({'CourseId': ObjectId(CourseId)}, {'Mark': 1, 'CheckIn': 1, 'Tags': 1})
        while (yield commentCur.fetch_next):
            n = commentCur.next_object()
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
                'CourseId': ObjectId(CourseId),
                'StudentId': int(self.get_body_argument('StudentId')),
                'NickName': self.get_body_argument('NickName'),
                'Content': self.get_body_argument('Content'),
                'CheckIn': int(self.get_body_argument('CheckIn')),
                'FinalTestType': self.get_body_argument('FinalTestType'),
                'Mark': int(self.get_body_argument('Mark')),
                'Time': int(time.time()),
            }
        except:
            return self.redirect('/course/%s?code=0' % CourseId)
        try:
            inf['Tags'] = self.get_body_argument('Tag').split(',')
        except:
            inf['Tags'] = []
        if (yield db.comments.find_one({
            'StudentId': inf['StudentId'],
            'CourseId': inf['CourseId'],
        })): return self.redirect('/course/%s?code=-1' % CourseId)
        yield db.comments.insert(inf)
        return self.redirect('/course/%s?code=1' % CourseId)


class CourseDetailPageHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, courseId, pageNum):
        comment = []
        commentCur = db.comments.find({'CourseId': ObjectId(courseId)}).sort([('Time', -1)]).skip(
                (int(pageNum) - 1) * 10).limit(10)
        while (yield commentCur.fetch_next):
            comment.append(commentCur.next_object())
        for i in comment:
            i['Time'] = datetimeformat(i['Time'])
        return self.render('course.datail.page.html', location='course', comment=comment)


class AboutHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render('about.html', location='about')


if __name__ == '__main__':
    db = db()
    options.parse_command_line()
    settings = {
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'template_path': os.path.join(os.path.dirname(__file__), 'templates'),
    }
    application = tornado.web.Application([
        (r'/', IndexHandler),
        (r'/course', CourseHandler),
        (r'/course/(\w{24})', CourseDetailHandler),
        (r'/course/(\w{24})/page/(\d+)', CourseDetailPageHandler),
        (r'/about', AboutHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
    ], **settings)
    application.listen(options.port, '127.0.0.1', xheaders=True)
    tornado.ioloop.IOLoop.instance().start()

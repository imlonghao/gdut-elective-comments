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
    def get(self):
        return self.render('course.html', location='course', classType=classType, classCampus=classCampus,
                           classAcademy=classAcademy)

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
            return self.send_error()
        yield db.courses.insert(inf)
        return


class CoursePageHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, pageNum):
        commentSort = []
        commentSortCur = db.comments.aggregate([{'$group': {'_id': '$CourseId', 'num': {'$sum': 1}}}])
        courses = []
        coursesCur = db.courses.find({'isPub': 1})
        while (yield commentSortCur.fetch_next):
            commentSort.append(commentSortCur.next_object())
        while (yield coursesCur.fetch_next):
            courses.append(coursesCur.next_object())
        for i in courses:
            try:
                i['CommentCount'] = [x['num'] for x in commentSort if x['_id'] == i['_id']][0]
            except:
                i['CommentCount'] = 0
        return self.render('course.page.html', location='course', courses=courses)


class CourseDetailHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, CourseId):
        course = yield db.courses.find_one({'_id': ObjectId(CourseId), 'isPub': 1})
        if not course: return self.send_error(404)
        course['Type'] = classType[course['Type']]
        course['Campus'] = classCampus[course['Campus']]
        course['Academy'] = classAcademy[course['Academy']]
        course['Count'] = yield db.comments.find({'CourseId': ObjectId(CourseId)}).count()
        tag = []
        tagcur = db.tags.find({'CourseId': ObjectId(CourseId)})
        while (yield tagcur.fetch_next):
            tag.append(tagcur.next_object())
        course['Tag'] = []
        for i in tag:
            course['Tag'] += i['Content']
        course['Tag'] = set(course['Tag'])
        Mark = []
        CheckIn = []
        commentCur = db.comments.find({'CourseId': ObjectId(CourseId)}, {'Mark': 1, 'CheckIn': 1})
        while (yield commentCur.fetch_next):
            n = commentCur.next_object()
            Mark.append(n['Mark'])
            CheckIn.append(n['CheckIn'])
        course['Mark'] = average(Mark)
        course['CheckIn'] = average(CheckIn)
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
            return self.send_error()
        if (yield db.comments.find_one({
            'StudentId': inf['StudentId'],
            'CourseId': inf['CourseId'],
        })): return self.send_error()
        tag = self.get_body_argument('Tag')
        yield db.tags.insert({
            'CourseId': ObjectId(CourseId),
            'Content': list(set(tag.split(','))),
            'StudentId': inf['StudentId'],
            'Time': int(time.time()),
        })
        yield db.comments.insert(inf)
        return


class CourseDetailPageHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, courseId, pageNum):
        comment = []
        commentCur = db.comments.find({'CourseId': ObjectId(courseId)}).sort([('Time', -1)])
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
        (r'/course/page/(\d+)', CoursePageHandler),
        (r'/course/(\w{24})', CourseDetailHandler),
        (r'/course/(\w{24})/page/(\d+)', CourseDetailPageHandler),
        (r'/about', AboutHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
    ], **settings)
    application.listen(options.port, '127.0.0.1', xheaders=True)
    tornado.ioloop.IOLoop.instance().start()

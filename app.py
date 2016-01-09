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


def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return time.strftime(format, time.gmtime(value))


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', location='index')


class CourseHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('course.html', location='course')


class CoursePageHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, pageNum):
        commentSort = []
        commentSortCur = db.comments.aggregate([{'$group': {'_id': '$CourseId', 'num': {'$sum': 1}}}])
        courses = []
        coursesCur = db.courses.find()
        while (yield commentSortCur.fetch_next):
            commentSort.append(commentSortCur.next_object())
        while (yield coursesCur.fetch_next):
            courses.append(coursesCur.next_object())
        for i in courses:
            try:
                i['CommentCount'] = [x['num'] for x in commentSort if x['_id'] == i['_id']][0]
            except:
                i['CommentCount'] = 0
        self.render('course.page.html', location='course', courses=courses)


class CourseDetailHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, courseId):
        course = yield db.courses.find_one({'_id': ObjectId(courseId)})
        self.render('course.detail.html', location='course', course=course)


class CourseDetailPageHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, courseId, pageNum):
        comment = []
        commentCur = db.comments.find({'CourseId': ObjectId(courseId)})
        while (yield commentCur.fetch_next):
            comment.append(commentCur.next_object())
        for i in comment:
            i['Time'] = datetimeformat(i['Time'])
        self.render('course.datail.page.html', location='course', comment=comment)


class AboutHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('about.html', location='about')


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

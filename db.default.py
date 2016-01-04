#!/usr/bin/env python3
import motor

USERNAME = ''
PASSWORD = ''
HOST = ''
PORT = 27017
DATABASE = ''


def db():
    return motor.MotorClient('mongodb://%s:%s@%s:%s/%s' % (
        USERNAME, PASSWORD, str(PORT),
        HOST, DATABASE
    ))[DATABASE]

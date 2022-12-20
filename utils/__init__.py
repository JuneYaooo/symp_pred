# -*- coding:utf-8 -*-
import random
from functools import wraps
from string import ascii_letters, digits
from flask import g, jsonify
import time


def random_string(size=10, chars=ascii_letters + digits):
    return ''.join(random.choice(chars) for _ in range(size))


def normal_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        role = g.normal
        if role is not None and role != 1:
            return None, 403
        return func(*args, **kwargs)

    return decorated_view


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        role = g.role
        if role is not None and role != 2:
            return None, 403
        return func(*args, **kwargs)

    return decorated_view


def get_days(start_ymd, end_ymd):
    start_timestamp = time.mktime(time.strptime(str(start_ymd), '%Y%m%d'))
    end_timestamp = time.mktime(time.strptime(str(end_ymd), '%Y%m%d'))

    days = []
    mid_timestamp = start_timestamp
    while mid_timestamp <= end_timestamp:
        mid_ymd = time.strftime('%Y%m%d', time.localtime(mid_timestamp))
        days.append(mid_ymd)
        mid_timestamp += 3600 * 24
    return days


if __name__ == '__main__':
    print(random_string(20))
    print(get_days('20221207', '20221213'))

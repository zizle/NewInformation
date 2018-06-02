# _*_ coding:utf-8 _*_
from flask import session, g
from info.models import User
import logging


def do_rank(num):
    """自定义模板过滤器"""
    if num == 1:
        return 'first'
    elif num == 2:
        return 'second'
    elif num == 3:
        return 'third'
    else:
        return ''


# 定义装饰器装饰视图函数，先检测用户的登录状态
def user_login_data(views_func):
    def wrapper(*args, **kwargs):
        """检测用户当前登录状态"""
        session_user_id = session.get('user_id')
        user = None
        if session_user_id:
            try:
                user = User.query.get(session_user_id)
            except Exception as e:
                logging.error(e)
        # 用全局g 变量保存用户
        g.user = user
        return views_func(*args, **kwargs)
    return wrapper

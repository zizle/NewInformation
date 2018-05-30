# _*_ coding:utf-8 _*_
from flask import render_template, current_app, session
from . import index_blue
from info.models import User
import logging


@index_blue.route('/favicon.ico', methods=['GET'])
def favicon():
    """主页title小logo"""
    return current_app.send_static_file('news/favicon.ico')


@index_blue.route('/')
def index():
    """主页"""
    # 登录状态展示
    # 判断登录状态保持
    session_user_id = session.get('user_id')
    session_user_mobile = session.get('mobile')
    session_user_nick_name = session.get('nick_name')
    # 校验参数, 查询用户数据，展示
    server_user = None
    if session_user_id and session_user_mobile and session_user_nick_name:
        try:
            server_user = User.query.get(session_user_id)
        except Exception as e:
            logging.ERROR(e)
    context = {
        'user': server_user
    }
    # 没有登录状态，显示登录/ 注册
    return render_template('index.html', context=context)

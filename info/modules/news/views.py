# _*_ coding:utf-8 _*_
from . import news_blue
from flask import render_template, session
from info.models import User, News
import logging


@news_blue.route('/detail/<news_id>')
def news_detail(news_id):
    """新闻详情页"""
    # 查询用户的登录状态
    session_user_id = session.get('user_id')
    user = None
    if session_user_id:
        try:
            user = User.query.get(session_user_id)
        except Exception as e:
            logging.error(e)
    # 查询新闻
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
    context = {
        'user': user,
        'news': news.to_dict()
    }
    return render_template('news/detail.html', context=context)


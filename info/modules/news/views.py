# _*_ coding:utf-8 _*_
from . import news_blue
from flask import render_template, g
from info.models import News
import logging
from info.utils.tools import user_login_data


@news_blue.route('/detail/<news_id>')
@user_login_data
def news_detail(news_id):
    """新闻详情页"""
    # 查询用户的登录状态(装饰器实现)，取出装饰器内g保存的user
    user = g.user
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


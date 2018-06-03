# _*_ coding:utf-8 _*_
from . import news_blue
from flask import render_template, g, request, jsonify, abort
from info.models import News
from info import response_code, db
import logging
from info.utils.tools import user_login_data


@news_blue.route('/collected', methods=['POST'])
@user_login_data
def news_collected():
    """用户收藏新闻"""
    # 检测用户的登录状态
    # 取出用户信息
    user = g.user
    # 判断当前用户是否登录
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='您还未登录')
    # 如果用户已登录，查看当前收藏的新闻
    user_collections = user.collection_news
    # 接收参数news_id
    news_id = request.json.get('news_id')
    # 拿着news_id去查询新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')
    # 如果有新闻，看用户是否收藏了
    # 没收藏
    if news not in user_collections:
        user_collections.append(news)
    # 同步数据库
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='收藏失败')
    return jsonify(errno=response_code.RET.OK, errmsg='收藏成功')


@news_blue.route('/cancel_collected', methods=['POST'])
@user_login_data
def cancel_collected():
    """取消收藏"""
    # 接收参数, news_id
    news_id = request.json.get('news_id')
    try:
        news_id = int(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # 拿着news_id去查询新闻
    try:
        news = News.query.filter(News.id == news_id).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询数据库失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='新闻不存在')
    # 判断news是否在用户收藏新闻列表里面
    # 用户收藏的新闻列表
    user_news_collects = g.user.collection_news
    if news in user_news_collects:
        user_news_collects.remove(news)
    # 同步数据库
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='取消失败!')
    return jsonify(errno=response_code.RET.OK, errmsg='取消成功!')


@news_blue.route('/detail/<news_id>')
@user_login_data
def news_detail(news_id):
    """新闻详情页"""
    # 1.查询用户的登录状态(装饰器实现)，取出装饰器内g保存的user
    user = g.user
    # 2.查询新闻
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
    if not news:
        abort(404)
    # 新闻存在，累加一次点击量
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(e)
    # 默认为未收藏
    is_collected = False
    if user:
        # 3 查询当前用户的收藏新闻
        user_collections = user.collection_news
        if news in user_collections:
            is_collected = True

    # 4. 查询点击排行
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        logging.error(e)

    context = {
        'user': user,
        'news': news.to_dict(),
        'is_collected': is_collected,
        'news_clicks': news_clicks
    }
    return render_template('news/detail.html', context=context)

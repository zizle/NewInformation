# _*_ coding:utf-8 _*_
from flask import render_template, current_app, g, request, jsonify, abort
from . import index_blue
from info.models import User, News, Category
import logging
from info import response_code, constants
from info.utils.tools import user_login_data


@index_blue.route('/favicon.ico', methods=['GET'])
def favicon():
    """主页title小logo"""
    return current_app.send_static_file('news/favicon.ico')


@index_blue.route('/')
@user_login_data
def index():
    """主页"""
    # 登录状态展示
    # 判断登录状态保持
    # 从g变量取出user
    server_user = g.user

    news_clicks = None
    try:
        # 点击排行数据渲染
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        logging.error(e)

    # 首页新闻分类标签查询
    categories = None
    try:
        categories = Category.query.all()
    except Exception as e:
        logging.error(e)

    context = {
        'user': server_user,
        'news_clicks': news_clicks,
        'categories': categories
    }
    # 没有登录状态，显示登录/ 注册
    return render_template('news/index.html', context=context)


@index_blue.route('/news_list', methods=['GET'])
def new_list():
    """展示主页新闻列表"""
    # 新闻列表展示
    # 接收client传入的参数，并验证
    cid = request.args.get('cid', 1)
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 6)
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        logging.error(e)
        abort(404)
    try:
        # 根据参数查询数据库
        if cid == 1:
            paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
        else:
            paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page, per_page, False)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='获取数据失败')
    # 当前页数
    cur_page = paginate.page
    # 总页数
    total_page = paginate.pages
    # 转换数据类型
    news_list = paginate.items
    news_list_dict = []
    user_list_dict = []
    for news in news_list:
        # 转为列表
        news_dict = news.to_basic_dict()
        # 加入列表
        news_list_dict.append(news_dict)
        if news.user:
            user_dict = news.user.to_dict()
            user_list_dict.append(user_dict)
        else:
            user_list_dict.append({})
    # 响应数据
    data = {
        'news_list': news_list_dict,
        'user_list': user_list_dict,
        'cur_page': cur_page,
        'total_page': total_page
    }
    # 拿到数据，响应
    return jsonify(errno=response_code.RET.OK, errmsg='OK', data=data)


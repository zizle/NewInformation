# _*_ coding:utf-8 _*_
from . import news_blue
from flask import render_template, g, request, jsonify, abort
from info.models import News, Comment, CommentLike
from info import response_code, db
import logging
from info.utils.tools import user_login_data


@news_blue.route('/detail/<news_id>')
@user_login_data
def news_detail(news_id):
    """新闻详情页"""
    try:
        news_id = int(news_id)
    except Exception as e:
        logging.error(e)
        abort(404)
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
    # 默认用户从没有点过任何赞
    user_like_comment_ids = []
    if user:
        # 3 查询当前用户的收藏新闻
        user_collections = user.collection_news
        if news in user_collections:
            is_collected = True
        # 查询当前用户点过的所有赞
        user_like_comments = CommentLike.query.filter(CommentLike.user_id==user.id).all()
        # 列表生成式得到这些赞对应的评论id
        user_like_comment_ids = [user_like_comment.comment_id for user_like_comment in user_like_comments ]

    # 4. 查询点击排行
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        logging.error(e)

    # 用当前news_id查询评论内容
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        logging.error(e)
    # 将所有评论to_dict()置于列表中
    comment_lists = []
    for comment in comments:
        comment_dict = comment.to_dict()
        # 添加标记当前用户是否点赞过这条新闻的这条赞 默认未点赞
        comment_dict['is_like'] = False
        # 当前评论id 在用户点过赞的评论id列表中 就是点赞
        if comment.id in user_like_comment_ids:
            comment_dict['is_like'] = True
        comment_lists.append(comment_dict)
    # 构造模板数据
    context = {
        'user': user,
        'news': news.to_dict(),
        'is_collected': is_collected,
        'news_clicks': news_clicks,
        'comment_lists': comment_lists
    }
    return render_template('news/detail.html', context=context)


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


@news_blue.route('/comment_news', methods=['POST'])
@user_login_data
def comment_news():
    """用户评论新闻"""
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='您还未登录')
    # 接收参数，news_id, comment_content
    news_id = request.json.get('news_id')
    comment_content = request.json.get('comment_content')
    if not all([news_id, comment_content]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    try:
        news_id = int(news_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # 预设news为空
    news = []
    try:
        # 查询评论的新闻是否在
        news = News.query.get(news_id)
    except Exception as e:
        logging.error(e)
    if not news:
        return jsonify(errno=response_code.RET.DBERR, errmsg='该新闻已不存在')
    # 新闻存在，创建评论
    news_comment = Comment()
    # 赋值属性
    news_comment.user_id = user.id
    news_comment.news_id = news_id
    news_comment.content = comment_content
    try:
        # 同步数据库
        db.session.add(news_comment)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='评论失败!')
    # 构造响应数据
    data = {'comment': news_comment.to_dict()}
    # 响应结果
    return jsonify(errno=response_code.RET.OK, errmsg='评论成功!', data=data)


@news_blue.route('/comment_comment', methods=['POST'])
@user_login_data
def comment_comment():
    """用户回复评论"""
    # 获取当前用户登录状态
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='您还未登录')
    # 接收参数 comment_id, comment_content并校验
    comment_parent_id = request.json.get('comment_id')
    comment_content = request.json.get('comment_content')
    # 由于表new_id不能为空
    news_id = request.json.get('news_id')
    try:
        news_id = int(news_id)
        comment_parent_id = int(comment_parent_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    # if not comment_id:返回评论不存在
    if not comment_parent_id:
        return jsonify(errno=response_code.RET.NODATA, errmsg='该评论不存在')
    # if comment_id 创建子评论
    children_comment = Comment()
    children_comment.user_id = user.id
    # 由于表中设计news_id不能为空, 需要添加
    children_comment.news_id = news_id
    children_comment.content = comment_content
    children_comment.parent_id = comment_parent_id
    # 同步数据库
    try:
        db.session.add(children_comment)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='评论失败!')
    # 构造响应数据
    data = {'children_comment': children_comment.to_dict()}
    # 响应结果
    return jsonify(errno=response_code.RET.OK, errmsg='评论成功!', data=data)


@news_blue.route('/like_comment', methods=['POST'])
@user_login_data
def like_comment():
    """用户点赞评论"""
    # 获取当前登录的用户信息
    user = g.user
    if not user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='您还没登录')
    # 用户登录了
    # 接收参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')
    # 校验参数
    try:
        comment_id = int(comment_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    if action not in ['add', 'remove']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    # 根据传入的comment_id 查看评论是否存在
    try:
        comment = Comment.query.filter(Comment.id == comment_id).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询评论出错')
    if not comment:
        return jsonify(errno=response_code.RET.DBERR, errmsg='评论不存在')
    try:
        # 查看用户的赞是否存在
        comment_like_model = CommentLike.query.filter(CommentLike.comment_id==comment_id, CommentLike.user_id==user.id).first()
    except Exception as e:
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询点赞出错')

    if action == 'add':
        if not comment_like_model:
            user_comment_like = CommentLike()
            user_comment_like.comment_id = comment_id,
            user_comment_like.user_id = user.id
            db.session.add(user_comment_like)
            # 累加点赞
            comment.like_count += 1
    else:
        if comment_like_model:
            db.session.delete(comment_like_model)
            # 减少点赞量
            comment.like_count -= 1
    # 同步数据库
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='点赞失败')
    if action == 'add':
        return jsonify(errno=response_code.RET.OK, errmsg='点赞成功')
    if action == 'remove':
        return jsonify(errno=response_code.RET.OK, errmsg='取消成功')






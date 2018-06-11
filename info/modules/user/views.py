# _*_ coding:utf-8 _*_

from . import user_blue
from flask import render_template, g, redirect, url_for, request, jsonify, session, current_app, abort
from info.utils.tools import user_login_data
from info import response_code, db, constants
from info.utils.file_storage import upload_file
from info.models import Category, News, User


@user_blue.route('modify_password')
def modify_password():
    """修改密码"""
    return render_template('news/user_modify_password.html')


@user_blue.route('/other_news_list')
def other_news_list():
    # 1.获取页数
    page = request.args.get("p", '1')
    other_id = request.args.get("user_id")

    # 2.校验参数
    try:
        p = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    if not all([page, other_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

    # 3.查询用户数据
    try:
        user = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=response_code.RET.NODATA, errmsg='用户不存在')

    # 4.分页查询
    try:
        paginate = News.query.filter(News.user_id == user.id, News.status==0).paginate(p, constants.OTHER_NEWS_PAGE_MAX_COUNT, False)
        # 获取当前页数据
        news_list = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户数据失败')

    # 5.构造响应数据
    news_dict_list = []
    for news_item in news_list:
        news_dict_list.append(news_item.to_review_dict())

    data = {
        "news_list": news_dict_list,
        "total_page": total_page,
        "current_page": current_page
    }

    # 6.渲染界面
    return jsonify(errno=response_code.RET.OK, errmsg='OK', data=data)


@user_blue.route('/other_info')
@user_login_data
def other_info():
    """其他用户概况"""
    # 1.获取登录用户信息
    login_user = g.user
    if not login_user:
        return redirect(url_for('index.index'))

    # 获取被登录用户关注的用户的信息
    other_id = request.args.get('user_id')
    if not other_id:
        abort(404)

    # 查询要展示的被关注的用户的信息
    other = None
    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    if not other:
        abort(404)

    # 判断关注和取消关注的显示
    is_followed = False
    if login_user and other:
        if other in login_user.followed:
            is_followed = True
    context = {
        'user': login_user.to_dict(),
        'other': other.to_dict(),
        'is_followed': is_followed
    }

    return render_template('news/other.html', context=context)


@user_blue.route('/user_followed')
@user_login_data
def user_followed():
    """我的关注"""
    # 1.获取登录用户信息
    login_user = g.user
    if not login_user:
        return redirect(url_for('index.index'))
    # 2.接受参数
    page = request.args.get('p', '1')
    # 3.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'
    # 4.查询登录用户关注的用户 （login_user.followed）
    followed_user_list = []
    total_page = 1
    current_page = 1
    try:
        paginate = login_user.followed.paginate(page,constants.USER_FOLLOWED_MAX_COUNT,False)
        followed_user_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    # 5.构造渲染数据
    followed_dict_list = []
    for followed_user in followed_user_list:
        followed_dict_list.append(followed_user.to_dict())

    context = {
        'users': followed_dict_list,
        'total_page': total_page,
        'current_page': current_page
    }
    return render_template('news/user_follow.html', context=context)


@user_blue.route('/news_list')
@user_login_data
def news_list():
    """发布的新闻列表"""
    user = g.user
    if not user:
        return render_template(url_for('index.index'))
    # 接收，校验参数
    page = request.args.get('p', '1')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'
    # 分页查询
    paginate = []
    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(page, constants.USER_RELEASE_MAX_NEWS, False)
    except Exception as e:
        current_app.logger.error(e)
    news_list = paginate.items
    cur_page = paginate.page
    total_page = paginate.pages
    # 构造参数
    context = {
        'news_list': news_list,
        'cur_page': cur_page,
        'total_page': total_page
    }
    # 渲染模板
    return render_template('news/user_news_list.html', context=context)


@user_blue.route('/release_news', methods=['GET', 'POST'])
@user_login_data
def release_news():
    """发布新闻"""
    user = g.user
    if not user:
        return render_template(url_for('index.index'))
    if request.method == 'GET':

        categories = []
        try:
            # 查找新闻分类
            categories = Category.query.filter(Category.id != 1).all()
        except Exception as e:
            current_app.logger.error(e)
        context = {
            'categories': categories
        }
        return render_template('news/user_news_release.html', context=context)
    if request.method == 'POST':
        # 接收参数, 校验参数
        title = request.form.get("title")
        category_id = request.form.get("category_id")
        source = "个人发布"
        digest = request.form.get("digest")
        content = request.form.get("content")
        index_image = request.files.get("index_image")
        if not all([title, source, digest, content, index_image, category_id]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        try:
            # 读取图片
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        # 上传图片
        image_key = upload_file(index_image)
        # 同步数据库
        news = News()
        news.user_id = user.id
        news.title = title
        news.source = source
        news.digest = digest
        news.content = content
        news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_key
        news.category_id = category_id
        # 审核状态
        news.status = 1
        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg='同步数据失败')
        # 返回结果
        return jsonify(errno=response_code.RET.OK, errmsg='发布成功!')


@user_blue.route('/user_collection')
@user_login_data
def user_collection():
    """用户收藏"""
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 接收参数
    page = request.args.get('p', '1')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'
    paginate = None
    try:
        # 查询用户收藏
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
    except Exception as e:
        current_app.logger.error(e)
    # 构造响应参数
    collection_lists = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    context = {
        'collection_lists': collection_lists,
        'total_page': total_page,
        'cur_page': current_page
    }
    return render_template('news/user_collection.html', context=context)


@user_blue.route('/change_psd', methods=['GET', 'POST'])
@user_login_data
def change_psd():
    """更改密码"""
    user = g.user
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    if request.method == 'POST':
        # 接收参数
        old_psd = request.json.get('old_password')
        new_psd = request.json.get('new_password')
        new_psd2 = request.json.get('new_password2')
        # 校验参数
        if not all([old_psd, new_psd, new_psd2]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        # 旧密码做对比
        if not user.check_password(old_psd):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='旧密码错误')
        # 修改密码
        user.password = new_psd
        # 同步数据库
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg='保存密码失败')
        session.pop('user_id')
        return jsonify(errno=response_code.RET.OK, errmsg='修改成功!请重新登录!')


@user_blue.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    """头像信息"""
    user = g.user
    if request.method == 'GET':
        context = {
            'user': user.to_dict() if user else None,
        }
        return render_template('news/user_pic_info.html', context=context)
    if request.method == 'POST':
        # 接收参数，校验参数
        avatar_file = request.files.get('avatar')
        try:
            avatar_data = avatar_file.read()
        except Exception as e:
            current_app.logger(e)
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        try:
            # 上传头像到存储平台
            key = upload_file(avatar_data)
        except Exception as e:
            return jsonify(errno=response_code.RET.THIRDERR, errmsg='上传失败')
        # 保存头像信息
        user.avatar_url = key
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg='头像保存失败')
        # 响应上传的结果
        # 构造响应数据
        data = {'avatar_url': constants.QINIU_DOMIN_PREFIX + key}
        print(data)
        return jsonify(errno=response_code.RET.OK, errmsg='上传成功', data=data)


@user_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    """基本资料"""
    # 可以不做判断的
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    # 渲染用户的基本信息
    if request.method == 'GET':
        context = {
            'user': user.to_dict(),
        }
        return render_template('news/user_base_info.html', context=context)
    # 修改用户的基本信息
    if request.method == 'POST':
        # 获取参数， 签名，昵称，性别
        new_signature = request.json.get('signature')
        new_nick_name = request.json.get('nick_name')
        new_gender = request.json.get('gender')
        # 校验参数
        if not all([new_gender, new_nick_name, new_signature]):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
        if new_gender not in ['MAN', 'WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
        # 修改用户的基本信息
        user.nick_name = new_nick_name
        user.signature = new_signature
        user.gender = new_gender
        # 同步数据库
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=response_code.RET.DBERR, errmsg='修改失败')
        # 修改了昵称，修改状态保持信息, 如果你状态保持用的是user.id是可以不修改的
        session['nick_name'] = new_nick_name
        # 响应结果
        return jsonify(errno=response_code.RET.OK, errmsg='修改成功')


@user_blue.route('/info')
@user_login_data
def user_info():
    """个人信息页面"""
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    context = {
        'user': user.to_dict()
    }
    return render_template('news/user.html', context=context)
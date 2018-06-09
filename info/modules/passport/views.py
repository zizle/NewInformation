# _*_ coding:utf-8 _*_

from . import passport_blue
from flask import request, abort, make_response, json, jsonify, session
from info.utils.captcha.captcha import captcha
from info import redis_store, constants, response_code, db
import logging
import re
import random
from info.libs.yuntongxun.sms import CCP
from info.models import User
from datetime import datetime


@passport_blue.route('/logout', methods=['GET'])
def logout():
    """退出登录"""
    # 清除cookie状态保持
    try:
        session.pop('user_id', None)
        session.pop('nick_name', None)
        session.pop('mobile', None)
        session.pop('is_admin', False)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='退出失败')
    # 响应结果
    return jsonify(errno=response_code.RET.OK, errmsg='您已退出！')


@passport_blue.route('/login', methods=['POST'])
def login():
    """用户登录"""
    # 接收客户端参数
    client_data_str = request.data
    client_data_dict = json.loads(client_data_str)
    # 获取参数
    client_mobile = client_data_dict.get('mobile')
    client_password = client_data_dict.get('password')
    # 验证客户端的参数齐全否，mobile合法否
    if not all([client_mobile, client_password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号或密码缺少')
    try:
        # 根据mobile查询数据库拿出server_user
        server_user = User.query.filter(User.mobile == client_mobile).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户失败')
    if not server_user:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='用户名或密码错误')
    # 对比password
    if not server_user.check_password(client_password):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='用户名或密码错误')
    # 写入session
    session['user_id'] = server_user.id
    session['nick_name'] = server_user.nick_name
    session['mobile'] = server_user.mobile
    # 响应情况
    return jsonify(errno=response_code.RET.OK, errmsg='登录成功!')


@passport_blue.route('/register', methods=['POST'])
def register():
    """注册用户"""
    # 接收浏览器传进来的参数mobile, sms_code, password
    client_json_str = request.data
    # 利用json转为字典
    client_json_dict = json.loads(client_json_str)
    # 获取参数
    client_mobile = client_json_dict.get('mobile')
    client_sms_code = client_json_dict.get('sms_code')
    client_password = client_json_dict.get('password')
    # 验证参数
    if not all([client_mobile, client_sms_code, client_password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='您的输入有误')
    # 判断手机号
    if not re.match(r'^1[35678][0-9]{9}$', client_mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号不合法')
    # 对比短信验证码
    try:
        # 从redis取出短信验证码
        server_sms_code = redis_store.get('SMSCode:'+client_mobile)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='数据库读取验证码失败')
    if server_sms_code.decode() != client_sms_code:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='短信验证码错误')
    # 通过验证，注册
    # 创建user
    user = User()
    # 给对象添加属性
    user.nick_name = client_mobile
    # 密码要加密
    user.password = client_password
    user.mobile = client_mobile
    # 记录最后一次登录
    user.last_login = datetime.now()
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(e)
    # 写入session，状态保持
    session['user_id'] = user.id
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    return jsonify(errno=response_code.RET.OK, errmsg='恭喜！注册成功！')


@passport_blue.route('/sms_code', methods=['POST'])
def sms_code():
    """发送短信验证码"""
    # 接收前端参数
    request_json_str = request.data
    request_json_dict = json.loads(request_json_str)
    mobile = request_json_dict.get('mobile')
    image_code_client = request_json_dict.get('imageCode')
    image_code_id = request_json_dict.get('imageCodeId')
    # 验证参数齐全
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='您的输入有误!')
    # 验证手机号是否合法
    if not re.match('^1[35678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='请输入合法的手机号!')
    try:
        # 取到redis中的验证码
        image_code_server = redis_store.get('ImageCode:'+image_code_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询验证码错误!')
    if not image_code_server:
        return jsonify(errno=response_code.RET.DBERR, errmsg='验证码已失效!')
    # 验证image_code是否正确
    if image_code_client.lower() != image_code_server.decode().lower():
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='验证码输入错误!')
    # 随机生成6位短信验证码
    sms_code = '%06d' % random.randint(0, 999999)
    print('短信验证码:', sms_code)
    # 发送短信
    # result = CCP().send_template_sms('15759566200', [sms_code, 3], 1)
    # # 判断发送的结果
    # if result != 0:
    #     logging.error(result)
    #     return jsonify(errno=response_code.RET.PARAMERR, errmsg='短信发送失败!')
    # # 保存短信码到redis便于下次验证
    try:
        redis_store.set('SMSCode:'+mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='短信码保存失败!')
    # 响应结果
    return jsonify(errno=response_code.RET.OK, errmsg='获取成功!')


@passport_blue.route('/image_code', methods=['GET'])
def image_code():
    """响应图片验证码"""
    # 拿到前端传过来的uuid, 唯一识别响应的图片
    image_code_id = request.args.get('imageCodeId')
    # uuid存在才给验证码
    if not image_code_id:
        # 向客户端抛出错误码
        abort(403)
    # 生成一个图片验证码
    name, text, image = captcha.generate_captcha()
    try:
        # 先保存到redis以便于下次做校验
        redis_store.set('ImageCode:'+image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存图片验证码失败')
    # 构造响应体
    response = make_response(image)
    # 设置响应头文件类型
    response.headers['Content-Type'] = 'image/jpg'
    print('图片验证码:', text)
    # 响应给前端
    return response

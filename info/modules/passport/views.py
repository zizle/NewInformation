# _*_ coding:utf-8 _*_

from . import passport_blue
from flask import request, abort, make_response, json, jsonify
from info.utils.captcha.captcha import captcha
from info import redis_store, constants, response_code
import logging
import re
import random
from info.libs.yuntongxun.sms import CCP


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
        logging.ERROR(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询验证码错误!')
    if not image_code_server:
        return jsonify(errno=response_code.RET.DBERR, errmsg='验证码已失效!')
    # 验证image_code是否正确
    if image_code_client.lower() != image_code_client.lower():
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='验证码输入错误!')
    # 随机生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999)
    # 发送短信
    result = CCP().send_template_sms('15759566200', [sms_code, 3], 1)
    # 判断发送的结果
    if result != 0:
        logging.ERROR(result)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='短信发送失败!')
    # 保存短信码到redis便于下次验证
    try:
        redis_store.set('SMSCode:'+mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        logging.ERROR(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='短信保存失败!')
    # 响应结果
    return jsonify(errno=response_code.RET.OK, errmsg='短信发送成功!')


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
        logging.DEBUG(e)
    # 构造响应体
    response = make_response(image)
    # 设置响应头文件类型
    response.headers['Content-Type'] = 'image/jpg'
    # 响应给前端
    return response

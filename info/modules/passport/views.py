# _*_ coding:utf-8 _*_

from . import passport_blue
from flask import request, abort, make_response
from info.utils.captcha.captcha import captcha
from info import redis_store, constants
import logging


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
        logging.debug(e)
    # 构造响应体
    response = make_response(image)
    # 设置响应头文件类型
    response.headers['Content-Type'] = 'image/jpg'
    # 响应给前端
    return response

# _*_ coding:utf-8 _*_

from . import passport_blue


@passport_blue.route('/image_code', methods=['GET'])
def image_code():
    """响应图片验证码"""
    pass

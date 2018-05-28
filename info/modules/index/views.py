# _*_ coding:utf-8 _*_

from . import index_bule


@index_bule.route('/')
def index():
    return '<h1>hello flask!</h1>'

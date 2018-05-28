# _*_ coding:utf-8 _*_
from flask import render_template, current_app
from . import index_blue


@index_blue.route('/favicon.ico', methods=['GET'])
def favicon():
    """主页title小logo"""
    return current_app.send_static_file('news/favicon.ico')


@index_blue.route('/')
def index():
    """主页"""
    return render_template('index.html')

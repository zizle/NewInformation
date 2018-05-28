# _*_ coding:utf-8 _*_
from flask import Flask
from config import configs
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler


def setup_log(level):
    """根据创建app时的创建环境加载日志的等级"""
    # 设置日志的记录等级
    logging.basicConfig(level=level)
    # 创建日志记录器, 指明日志保存的路径, 每个日志文件的最大大小,保存日志的文件上限个数
    file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式
    # formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # 为刚创建的日志记录器设置日志格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象(flask app使用的)添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# 创建连接MySQL全局对象
db = SQLAlchemy()


def create_app(config_name):
    """工厂模式创建app"""
    # 设置日志
    setup_log(configs[config_name].LOGGING_LEVEL)
    app = Flask(__name__)
    app.config.from_object(configs[config_name])
    # 传入app
    db.init_app(app)
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)
    # 开启csrf保护
    CSRFProtect(app)
    Session(app)
    # 导入蓝图，避免过早导入蓝图失败(有些参数还没创建)，app注册的地方导入
    from info.modules.index import index_blue
    # 注册主页路由给app
    app.register_blueprint(index_blue)
    # 注册passport蓝图
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    return app

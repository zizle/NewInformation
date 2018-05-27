# _*_ coding:utf-8 _*_
from flask import Flask
from config import configs
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

# 创建连接MySQL全局对象
db = SQLAlchemy()


def create_app(config_name):
    """工厂模式创建app"""
    app = Flask(__name__)
    app.config.from_object(configs[config_name])
    # 传入app
    db.init_app(app)
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)
    # 开启csrf保护
    CSRFProtect(app)
    Session(app)
    return app
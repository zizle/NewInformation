# _*_ coding:utf-8 _*_

from datetime import timedelta
from redis import StrictRedis
import logging


class Config(object):
    DEBUG = True
    # 连接数据库MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql+pymsql://root:mysql@127.0.0.1:3306/db_information_github'
    # 设置不追踪数据库改变，提高点性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis 数据库配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 设置session秘钥
    SECRET_KEY = 'abc'
    # 设置session的存活时间
    PERMANENT_SESSION_LIFETIME = timedelta(days=3)
    # 设置session用什么存储
    SESSION_TYPE = 'redis'
    # 设置session存储在后端的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # session使用秘钥
    SESSION_USE_SIGNER = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymsql://root:mysql@127.0.0.1:3306/db_information_github'
    LOGGING_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymsql://root:mysql@127.0.0.1:3306/db_pro_information_github'
    LOGGING_LEVEL = logging.ERROR


class UnittestConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymsql://root:mysql@127.0.0.1:3306/db_test_information_github'
    LOGGING_LEVEL = logging.DEBUG


configs = {
    'dev': DevelopmentConfig,
    'pro': ProductionConfig,
    'unit': UnittestConfig
}
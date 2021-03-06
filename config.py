#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date        : 2022-06-07 14:44:24
# @Author      : junsircoding
# @File        : config.py
# @Info        : 
# @Last Edited : 2022-06-07 14:44:24

"""
项目配置文件
"""

import logging
from redis import StrictRedis


class Config(object):
    """项目配置"""
    SECRET_KEY = ""

    # 为数据库添加配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 在请求结束时候, 如果指定此配置为 True , 那么 SQLAlchemy 会自动执行一次 db.session.commit()操作
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Redis的配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # Session 保存配置
    SESSION_TYPE = "redis"
    # 开启 Session 签名
    SESSION_USE_SIGNER = True
    # 指定 Session 保存的 redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置需要过期
    SESSION_PERMANENT = False
    # 设置过期时间
    PERMANENT_SESSION_LIFETIME = 86400 * 7

    # 设置日志等级
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):
    """开发环境"""
    ENV = "development"
    DEBUG = True
    # 暂时将csrf设置为不检测
    WTF_CSRF_ENABLED = False
    SESSION_CACHE = {
        'host': Config.REDIS_HOST,
        'port': Config.REDIS_PORT,
        'password': '',
        'db': 1
    }
    VERIFY_CODE_CACHE = {
        'host': Config.REDIS_HOST,
        'port': Config.REDIS_PORT,
        'password': '',
        'db': 2
    }


class ProductionConfig(Config):
    """生产环境"""
    ENV = "production"
    DEBUG = False
    LOG_LEVEL = logging.WARNING


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

"""
项目初始化
"""

import logging
from config import config
from flask import Flask, render_template, g
# 可以用来指定 session 保存的位置
from flask_wtf import CSRFProtect
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from redis import StrictRedis
from .utils.common import user_login_data


# 初始化数据库
db = SQLAlchemy()

# 变量注释,指定变量类型(使用全局变量无法智能提示时)
redis_store = None  # type: StrictRedis


def setup_log(config_name):
    """自定义日志
    
    Args:
        config_name(str): 配置文件名称, 根据环境不同而不同
    """
    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)
    # 创建日志记录器, 指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/server.log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """创建 Flask 应用, 注册蓝图等
    
    Args:
        config_name(str): 配置文件名称, 根据环境不同而不同
    Returns:
        (FLask): Flask 应用
    """
    # 配置日志,并且传入配置名字, 获取指定配置所对应的日志等级
    setup_log(config_name)

    # TODO: 创建 Flask 对象
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config[config_name])
    # 通过 app 初始化
    db.init_app(app)
    # 初始化 Redis 存储对象
    global redis_store
    redis_store = StrictRedis(
        host=config[config_name].REDIS_HOST,
        port=config[config_name].REDIS_PORT,
        decode_responses=True
    )
    # 开启当前项目 CSRF 保护, 只做服务器验证功能
    CSRFProtect(app)
    # 设置session保存指定位置
    Session(app)

    # TODO: 注册蓝图
    # index 模块
    from .modules.index import index_blu
    app.register_blueprint(index_blu)
    # passport 模块
    from .modules.passport import passport_blu
    app.register_blueprint(passport_blu, url_prefix='/passports')

    # news 模块
    from .modules.news import news_blu
    app.register_blueprint(news_blu, url_prefix='/news')

    # user 模块
    from .modules.profile import profile_blu
    app.register_blueprint(profile_blu, url_prefix='/user')

    # admin 模块
    from .modules.admin import admin_blu
    app.register_blueprint(admin_blu, url_prefix='/admin')

    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class, "indexClass")

    @app.errorhandler(404)
    @user_login_data
    def page_not_found(_):
        user = g.user
        data = {"user": user.to_dict() if user else None}
        return render_template('news/404.html', data=data)

    return app

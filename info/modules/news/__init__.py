"""
news 模块蓝图
"""

from flask import Blueprint

# 创建蓝图对象
news_blu = Blueprint('news', __name__)

from . import views
"""
profile 模块蓝图
"""

from flask import Blueprint

# 创建蓝图对象
profile_blu = Blueprint('profile', __name__)

from . import views
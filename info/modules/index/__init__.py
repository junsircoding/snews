"""
index 模块蓝图
"""

from flask import Blueprint

# 创建蓝图对象
index_blu = Blueprint('index', __name__)

# 蓝图装饰完接口后再导入
from . import views
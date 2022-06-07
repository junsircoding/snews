#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date        : 2022-06-07 10:27:31
# @Author      : junsircoding
# @File        : info/modules/index/__init__.py
# @Info        : 
# @Last Edited : 2022-06-07 14:44:24

"""
index 模块蓝图
"""

from flask import Blueprint

# 创建蓝图对象
index_blu = Blueprint('index', __name__)

# 蓝图装饰完接口后再导入
from . import views

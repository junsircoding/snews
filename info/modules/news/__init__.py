#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date        : 2022-06-07 10:27:31
# @Author      : junsircoding
# @File        : info/modules/news/__init__.py
# @Info        : 
# @Last Edited : 2022-06-07 14:44:24

"""
news 模块蓝图
"""

from flask import Blueprint

# 创建蓝图对象
news_blu = Blueprint('news', __name__)

from . import views

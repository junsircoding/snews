#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date        : 2022-06-07 10:27:31
# @Author      : junsircoding
# @File        : info/modules/passport/__init__.py
# @Info        : 
# @Last Edited : 2022-06-07 14:44:24

from flask import Blueprint

# 创建蓝图对象
passport_blu = Blueprint('passport', __name__)

from . import views

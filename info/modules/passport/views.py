"""
passport 模块接口
"""

import random
from flask import jsonify, current_app
from flask import Response, request, session
from info import db
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.common import redis_client
from info.utils.constants import *
from . import passport_blu


@passport_blu.route('/image_code')
def get_image_code():
    """生成图片验证码

    Returns:
        图片验证码
    """
    # 1. 接收
    image_code = request.args.get('imageCode')
    # 2. 验证
    # 非空验证
    if not all([image_code]):
        return jsonify(errno=RETCODE.IMAGECODEERR, errmsg='图片验证码未接收到')
    # 3. 处理
    # 3.1 调用 captcha 生成验证码
    _, code, image = captcha.generate_captcha()
    # 3.2 连接 Redis, 将验证码存入 Redis, 设置过期时间
    redis_con = redis_client()
    pip = redis_con.pipeline()
    pip.setex('image_code', IMAGE_CODE_EXPIRES, code)
    pip.execute()
    # 3.3 控制台打印验证码字符
    current_app.logger.info('图片验证码为：%s' % code)
    # 4. 响应
    resp = Response(image, mimetype="image/jpeg")
    return resp


@passport_blu.route('/sms_code', methods=["POST"])
def send_sms_code():
    """接收 Ajax 发送的 json 数据并进行校验
    之后生成短信验证码并调用第三方接口发送验证码
    根据结果返回状态信息

    Returns: 
        状态信息
    """
    # 1. 接收图片验证码
    data = request.get_json()
    mobile = data['mobile'],
    image_code = data['image_code'],
    image_code_id = data['image_code_id']
    # 2. 验证
    # 2.1 非空验证
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 2.3 图片验证码是否正确
    redis_con = redis_client()
    code = (redis_con.get('image_code'))
    code = bytes.decode(code)
    image_code = str(image_code[0]).upper()
    if image_code != code:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='图形验证码错误')
    # 2.4 判断手机号是否发过短信
    sms_flag = redis_con.get('sms_flag_' + str(mobile))
    if sms_flag:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='已经向此手机发送过短信')
    # 3. 处理
    # 3.1 生成六位随机数
    sms_code = '%06d' % random.randint(0, 999999)
    # 存入 Redis
    pip = redis_con.pipeline()
    pip.setex('sms_' + str(mobile[0]), SMS_CODE_EXPIRES, sms_code)
    pip.setex('sms_flag_' + str(mobile[0]), SMS_FLAG_EXPIRES, 1)
    pip.execute()
    # 调用容联云通讯, 发送短信验证码
    # 控制台打印验证码
    current_app.logger.info('手机验证码为：%s' % sms_code)
    # 4.响应
    return jsonify(errno=RETCODE.OK, errmsg='ok')


@passport_blu.route('/register', methods=["POST"])
def register():
    """注册

    Returns:
    """
    # 1. 获取参数
    data = request.get_json()
    mobile = data['mobile']
    password = data['password']
    smscode = data['smscode']
    # 2. 校验非空
    if not all([mobile, password, smscode]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 3. 一个手机号只能注册一次
    user = User.query.filter(User.mobile == mobile).first()
    if user:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='该手机号已经注册, 请直接登录')
    # 4. 从 Redis 中获取指定手机号对应的短信验证码
    redis_cli = redis_client()
    sms_code_redis = redis_cli.get('sms_' + mobile)
    if not sms_code_redis:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='短信验证码已过期')
    sms_code_redis = bytes.decode(sms_code_redis)
    # 5. 校验验证码
    if not sms_code_redis == smscode:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='短信验证码错误')
    # 6. 强制过期
    redis_cli.delete('sms_' + mobile)
    # 7. 初始化 User 模型, 并设置数据并添加到数据库
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = password
    user.is_admin = False

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
    # 8. 保存用户登录状态
    session["user_id"] = user.id
    # 9. 返回注册结果
    return jsonify(errno=RETCODE.OK, errmsg='ok')


@passport_blu.route('/login', methods=["POST"])
def login():
    """登录功能

    Returns:
    """
    # 1. 获取参数
    data = request.get_json()
    mobile = data['mobile']
    password = data['password']
    current_app.logger.info(password)
    # 2. 判断非空
    if not all([mobile, password]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 3. 从数据库查询出指定的用户
    user = User.query.filter(User.mobile == mobile).first()
    # 4. 校验是否有用户
    if not user:
        return jsonify(errno=RETCODE.USERERR, errmsg='未找到该用户')
    # 5. 校验密码是否正确
    if not user.check_password(password):
        return jsonify(errno=RETCODE.USERERR, errmsg='密码错误')
    # 6. 保存用户登录状态
    session["user_id"] = user.id
    # 7. 登录成功返回
    return jsonify(errno=RETCODE.OK, errmsg='login ok')


@passport_blu.route("/logout", methods=['POST'])
def logout():
    """清除 Session 中的对应登录之后保存的信息

    Returns:
    """
    session.clear()
    return jsonify(errno=RETCODE.OK, errmsg='注销成功')

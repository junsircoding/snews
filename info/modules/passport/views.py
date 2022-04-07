"""
passport 模块接口
"""

import random
from flask import jsonify
from flask import request, Response, session
from info import db
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.cachegetter import verify_code_cache
from info.utils.response_code import RETCODE
from . import params
from . import passport_blu


@passport_blu.route('/image_code')
def get_image_code():
    """生成图片验证码

    Returns:
        图片验证码
    """
    # 1.接收
    image_code = request.args.get('image_Code')
    # 2.验证
    # 非空验证
    if not all([image_code]):
        return jsonify(errno=RETCODE.IMAGECODEERR, errmsg='图片验证码未接收到')
    # 3.处理
    # 3.1调用captcha生成验证码
    text, code, image = captcha.generate_captcha()
    # 3.2连接redis, 将验证码存入redis, 设置过期时间
    redis_con = verify_code_cache()
    pip = redis_con.pipeline()
    pip.setex('image_code', params.IMAGE_CODE_EXPIRES, code)
    pip.execute()
    # 3.3控制台打印验证码字符
    print('图片验证码为：%s' % code)
    # 4.响应
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
    # 1.接收
    data = request.get_json()
    mobile = data['mobile'],
    imageCode = data['image_code'],
    imageCodeId = data['image_code_id']
    # 2.验证
    # 2.1非空验证
    if not all([mobile, imageCode, imageCodeId]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 2.3图片验证码是否正确
    redis_con = verify_code_cache()
    code = (redis_con.get('image_code'))
    code = bytes.decode(code)
    imageCode = str(imageCode[0]).upper()
    if imageCode != code:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='图形验证码错误')
    # 2.4判断手机号是否发过短信
    sms_flag = redis_con.get('sms_flag_' + str(mobile))
    if sms_flag:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='已经向此手机发送过短信')

    # 3.处理
    # 3.1生成六位随机数
    sms_code = '%06d' % random.randint(0, 999999)
    # 存入redis
    pip = redis_con.pipeline()
    pip.setex('sms_' + str(mobile[0]), params.SMS_CODE_EXPIRES, sms_code)
    pip.setex('sms_flag_' + str(mobile[0]), params.SMS_FLAG_EXPIRES, 1)
    pip.execute()
    # 调用容联云通讯
    # 控制台打印验证码
    print('手机验证码为：%s' % sms_code)
    # 4.响应
    return jsonify(errno=RETCODE.OK, errmsg='ok')


@passport_blu.route('/register', methods=["POST"])
def register():
    """注册功能

    Returns:
    """
    # 1. 获取参数
    data = request.get_json()
    mobile = data['mobile']
    password = data['password']
    # smscode = data['smscode']
    # 2.校验非空
    # if not all([mobile, password, smscode]):
    if not all([mobile, password]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 3. 从 Redis 中获取指定手机号对应的短信验证码
    # redis_cli = verify_code_cache()
    # sms_code_redis = redis_cli.get('sms_' + mobile)
    # if not sms_code_redis:
    #     return jsonify(errno=RETCODE.PARAMERR, errmsg='短信验证码已过期')
    # sms_code_redis = bytes.decode(sms_code_redis)
    # 4.校验验证码
    # if not sms_code_redis == smscode:
    #     return jsonify(errno=RETCODE.PARAMERR, errmsg='短信验证码错误')
    # 5.强制过期
    # redis_cli.delete('sms_' + mobile)
    # 4. 初始化 user 模型, 并设置数据并添加到数据库
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
        print(e)
    # 5. 保存用户登录状态
    session["user_id"] = user.id
    # 6. 返回注册结果
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
    # 2.判断非空
    if not all([mobile, password]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 2. 从数据库查询出指定的用户
    user = User.query.filter(User.mobile == mobile,
                             User.password_hash == password).all()
    # 3. 校验密码
    if user:
        user = user[0]
    else:
        user = None

    # 4. 保存用户登录状态
    session["user_id"] = user.id
    # 5. 登录成功返回
    return jsonify(errno=RETCODE.OK, errmsg='login ok')


@passport_blu.route("/logout", methods=['POST'])
def logout():
    """清除 Session 中的对应登录之后保存的信息
    
    Returns:
    """
    session.clear()
    return jsonify(errno=RETCODE.OK, errmsg='logout ok')

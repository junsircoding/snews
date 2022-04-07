"""
profile 模块接口
"""

import os
import uuid
from flask import render_template, redirect, abort, current_app, g
from flask import jsonify, request, session
from info import constants
from info.models import db
from info.models import User, Category, News, tb_user_collection
from info.utils.common import user_login_data
from info.utils.response_code import RETCODE
from . import profile_blu


@profile_blu.route('/info')
@user_login_data
def user_info():
    """用户个人信息"""
    user = g.user
    if user:
        # 如果用户已登录则进入个人中心
        # 返回用户数据
        return render_template('news/user.html', data={"user": g.user.to_dict()})
    else:
        # 如果没有登录, 跳转主页
        return redirect('/')


@profile_blu.route('/base_info', methods=["GET", "POST"])
@user_login_data
def base_info():
    """用户基本信息

    Returns:
    """
    user = g.user
    # 不同的请求方式, 做不同的事情
    # 如果是 GET 请求, 返回用户数据
    if request.method == 'GET':
        if not user.signature:
            user.signature = '请输入个性签名^_^'
        return render_template('news/user_base_info.html', data={"user": user.to_dict()})
    else:
        # 修改用户数据
        # 获取传入参数
        data = request.get_json()
        signature = data['signature']
        nick_name = data['nick_name']
        gender = data['gender']
        # 校验参数
        if not all([signature, nick_name, gender]):
            return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
        # 修改用户数据
        User.query.filter_by(id=user.id).update({
            'signature': signature,
            'nick_name': nick_name,
            'gender': gender

        })
        db.session.commit()
        # 返回
        return jsonify(errno=RETCODE.OK, errmsg='ok')


@profile_blu.route('/pic_info', methods=["GET", "POST"])
@user_login_data
def pic_info():
    """上传图片修改头像
    """
    user = g.user
    # 如果是 GET 请求,返回用户数据
    if request.method == 'GET':
        return render_template('news/user_pic_info.html', data={"user_info": user.to_dict()})
    else:
        # 如果是POST请求表示修改头像
        # 1. 获取到上传的图片
        f = request.files['avatar']
        # 2. 上传头像
        info_dir_path = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                )
            )
        images_path = '/static/news/images/'
        avatar_file_name = str(uuid.uuid4())
        avatar_url = info_dir_path + images_path + avatar_file_name
        f.save(avatar_url)
        current_app.logger.info(info_dir_path)
        current_app.logger.info(images_path)
        current_app.logger.info(avatar_file_name)
        avatar_url = info_dir_path[32:len(info_dir_path):1] + images_path + avatar_file_name
        current_app.logger.info(avatar_url)
        # 3. 保存头像地址
        User.query.filter_by(id=user.id).update({'avatar_url': avatar_url})
        db.session.commit()
        # 拼接 URL 并返回数据
        data = {
            'avatar_url': avatar_url
        }
        return jsonify(errno=RETCODE.OK, errmsg='ok', data=data)


@profile_blu.route('/pass_info', methods=["GET", "POST"])
@user_login_data
def pass_info():
    """修改密码
    """
    user = g.user
    # GET请求,返回
    if request.method == "GET":
        return render_template('news/user_pass_info.html')
    # 1. 获取参数
    data = request.get_json()
    old_password = data['old_password']
    new_password = data['new_password']
    new_password2 = data['new_password2']
    # 2. 校验参数
    if not all([old_password, new_password, new_password2]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 3. 判断旧密码是否正确
    if not user.check_password(old_password):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='旧密码输入错误')
    # 4. 确认密码
    if new_password != new_password2:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='两次密码输入不一致')
    # 5. 设置新密码
    user.password = new_password
    db.session.commit()
    # 6. 强制注销, 重新登录
    session.clear()
    # 返回
    return jsonify(errno=RETCODE.OK, errmsg='修改成功, 请重新登录')


@profile_blu.route('/collection')
@user_login_data
def user_collection():
    user = g.user
    # 1. 获取参数
    # 当前页数
    page = request.args.get('p')
    collections = None
    total_page = None
    # 2. 判断参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(f"获取分页配置时发生异常: {e}")
        page = 1
    # 3. 查询用户指定页数的收藏的新闻
    # 进行分页数据查询
    try:
        paginate = user.collection_news.paginate(
            page,
            constants.USER_COLLECTION_MAX_NEWS,
            False
        )
        collections = paginate.items
        page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    # 收藏列表
    data = {
        'collections': collections,
        'current_page': page,
        'total_page': total_page
    }
    # 返回数据
    return render_template('news/user_collection.html', data=data)


@profile_blu.route('/news_release', methods=["GET", "POST"])
@user_login_data
def news_release():
    # GET请求
    if request.method == 'GET':
        # 1. 加载新闻分类数据
        # 2. 移除最新分类
        categories = Category.query.filter(Category.id != '1').all()
        # 返回数据
        data = {
            'categories': categories
        }
        return render_template('news/user_news_release.html', data=data)

    # 1. 获取要提交的数据
    data = request.form
    content = data.get('content')
    title = data.get('title')
    category_id = data.get('category_id')
    digest = data.get('digest')
    try:
        index_image = request.files['index_image']
    except Exception as e:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='请选择封面图片')
    source = data.get('source')

    # 校验参数
    if not all([title, category_id, digest, index_image, content, source]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 3.取到图片, 将图片上传到七牛云
    try:
        a = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        b = '/static/news/images/'
        c = str(uuid.uuid4())
        avatar_url = a + b + c
        index_image.save(avatar_url)
        index_image_url = a[32:len(a):1] + b + c
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RETCODE.PARAMERR, errmsg="参数有误")

    # 保存数据
    new_news = News()
    new_news.title = title
    new_news.category_id = category_id
    new_news.digest = digest
    new_news.index_image_url = index_image_url
    new_news.content = content
    new_news.source = source
    # 新闻状态,将新闻设置为1代表待审核状态
    new_news.status = constants.NEWS_NOT_CHECK
    new_news.user_id = g.user.id

    db.session.add(new_news)
    db.session.commit()
    # 返回
    return jsonify(errno=RETCODE.OK, errmsg='ok')


@profile_blu.route('/news_list')
@user_login_data
def user_news_list():
    user = g.user
    page = request.args.get("p", 1)

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news = []
    current_page = 1
    total_page = 1
    try:
        paginate = News.query.filter(
            News.user_id == user.id
        ).order_by(
            News.create_time.desc()
        ).paginate(
            page,
            constants.ADMIN_NEWS_PAGE_MAX_COUNT,
            False
        )
        news = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for new in news:
        news_dict = {
            'id': new.id,
            'title': new.title,
            'status': new.status,
            'create_time': new.create_time,
            'reason': new.reason
        }
        news_dict_list.append(news_dict)

    data = {
        "total_page": total_page,
        "current_page": current_page,
        'news_list': news_dict_list
    }
    return render_template('news/user_news_list.html', data=data)


@profile_blu.route('/user_follow')
@user_login_data
def user_follow():
    # 获取页数
    p = request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        p = 1
        return jsonify(errno=RETCODE.PARAMERR, errmsg='出错')

    user = g.user

    follows = []
    current_page = 1
    total_page = 1
    try:
        paginate = user.followed.paginate(
            p,
            constants.USER_FOLLOWED_MAX_COUNT,
            False
        )
        # 获取当前页数据
        follows = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='出错')

    user_dict_li = []

    for follow_user in follows:
        user_dict_li.append(follow_user.to_dict())
    data = {
        "users": user_dict_li,
        "total_page": total_page,
        "current_page": current_page
    }
    return render_template('news/user_follow.html', data=data)


@profile_blu.route('/other_info')
@user_login_data
def other_info():
    user = g.user

    # 去查询其他人的用户信息
    other_id = request.args.get("user_id")

    if not other_id:
        abort(404)

    # 查询指定id的用户信息
    other = None
    try:
        other = User.query.get(other_id)
    except Exception as e:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='出错')

    if not other:
        abort(404)

    # 判断当前登录用户是否关注过该用户
    is_followed = False
    if other and user:
        if other in user.followed:
            is_followed = True

    data = {
        "is_followed": is_followed,
        "user": g.user.to_dict() if g.user else None,
        "other_info": other.to_dict()
    }
    return render_template('news/other.html', data=data)


@profile_blu.route('/other_news_list')
def other_news_list():
    """返回指定用户的发布的新闻"""

    # 1. 取参数
    other_id = request.args.get("user_id")
    page = request.args.get("p", 1)

    # 2. 判断参数
    try:
        page = int(page)
    except Exception as e:
        return jsonify(errno=RETCODE.PARAMERR, errmsg="参数错误")

    try:
        other = User.query.get(other_id)
    except Exception as e:
        return jsonify(errno=RETCODE.DBERR, errmsg="数据查询失败")

    if not other:
        return jsonify(errno=RETCODE.NODATA, errmsg="当前用户不存在")

    try:
        paginate = other.news_list.paginate(
            page, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取当前页数据
        news_li = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        return jsonify(errno=RETCODE.DBERR, errmsg="数据查询失败")

    news_dict_list = []
    for news_item in news_li:
        news_dict_list.append(news_item.to_basic_dict())

    data = {
        "news_list": news_dict_list,
        "total_page": total_page,
        "current_page": current_page
    }

    # print(news_dict_list)
    return jsonify(errno=RETCODE.OK, errmsg="OK", data=data)

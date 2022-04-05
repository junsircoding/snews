"""
news 模块接口
"""

from flask import render_template, g, current_app
from flask import jsonify, request
from info import db, models
from info.models import News, User, Comment, CommentLike
from info.utils.response_code import RETCODE
from info.utils.common import user_login_data
from . import news_blu


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """新闻详情
    
    Args:
        news_id(int): 新闻 ID
    Returns:
        (function): 新闻详情渲染网页
    """

    # 获取当前登录用户对象
    user = g.user
    # 按照点击次数前8排序
    news_dict = News.query.order_by(News.clicks.desc()).limit(8).all()

    # 进入详情页后要更新新闻的点击次数
    new_click = News.query.get(news_id)
    new_click.clicks = new_click.clicks + 1
    db.session.add(new_click)
    db.session.commit()

    # 判断用户是否收藏过该新闻
    if user:
        # 查询出该用户收藏的新闻列表
        news_list = user.collection_news.all()
        # 收藏标识默认为False
        is_collected = False
        # 遍历该列表, 如果当前浏览的新闻在当前登录用户的收藏列表里, 则表示已收藏, is_collected为True
        news_id_l = [i.id for i in news_list]
        if news_id in news_id_l:
            is_collected = True
    else:
        is_collected = False

    # 获取当前新闻所有评论, 按时间排序
    comment_list = Comment.query.filter(
        Comment.news_id == news_id
    ).order_by(
        Comment.create_time.desc()
    ).all()
    comments = []
    if user:
        for c in comment_list:
            # 从 CommentLike 表中查询出所有当前新闻被点赞的条目
            comment_like_list = CommentLike.query.filter(
                CommentLike.comment_id == c.id
            ).all()
            # 该评论是否被点赞
            is_like = False
            like_list = [i.user_id for i in comment_like_list]
            if user.id in like_list:
                is_like = True
            comment_item = {
                'user': User.query.filter(User.id == c.user_id).all()[0],
                'content': c.content,
                'parent': {
                    'content': c.parent.content,
                    'user': User.query.filter(User.id == c.parent.user_id).all()[0]
                } if c.parent else None,
                'news_id': news_id,
                'create_time': c.create_time,
                'id': c.id,
                'is_like': is_like,
                'like_count': c.like_count
            }
            comments.append(comment_item)

    # 查询新闻数据
    news = News.query.filter(News.id == news_id).all()
    if news:
        news = {
            'comments_count': len(comment_list),
            'title': news[0].title,
            'create_time': news[0].create_time,
            'source': news[0].source,
            'id': news[0].id,
            'content': news[0].content,
            'author': User.query.filter(User.id == news[0].user_id).first().to_dict()
        }
    else:
        news = None

    author_id = News.query.filter(News.id == news_id).all()[0].user_id
    is_followed = User.query.filter(User.id == author_id)[0].followers.all()
    # 当前登录用户是否关注当前新闻作者
    if is_followed:
        is_followed = True
    else:
        is_followed = False

    # 返回数据
    data = {
        "user": user.to_dict() if user else None,
        "news": news,
        "is_collected": is_collected if user else None,
        "comments": comments,
        "news_dict": news_dict,
        'is_followed': is_followed
    }
    return render_template('news/detail.html', data=data)


@news_blu.route('/news_collect', methods=['POST'])
@user_login_data
def news_collect():
    """
    新闻收藏
    Returns:
    """
    user = g.user
    # 获取参数, {news_id: "8", action: "cancel_collect"}
    data = request.get_json()
    news_id = data['news_id']
    action = data['action']

    # 判断参数
    if action == 'cancel_collect':
        # 取消收藏, 即删除info_user_collection表中对应的行
        news = News.query.filter(News.id == news_id).all()[0]
        user.collection_news.remove(news)
        db.session.add(user)
        db.session.commit()
    else:
        # 收藏, 即在info_user_collection表中添加对应的行
        # 查询出当前浏览新闻对象
        news = News.query.filter(News.id == news_id).all()[0]
        user.collection_news.append(news)
        db.session.add(user)
        db.session.commit()

    # 查询新闻, 并判断新闻是否存在
    # 收藏/取消收藏
    return jsonify(errno=RETCODE.OK, errmsg='ok')


@news_blu.route('/news_comment', methods=['POST'])
@user_login_data
def add_news_comment():
    """
    添加评论
    Returns:
    """
    # 用户是否登录
    user = g.user
    # 获取参数, {news_id: news_id, comment: news_comment}
    data = request.get_json()
    news_id = data['news_id']
    comment = data['comment']
    try:
        parent_id = data['parent_id']
    except:
        parent_id = None
    # 判断参数是否正确
    if not all([news_id, comment]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 查询新闻是否存在并校验
    new = News.query.filter(News.id == news_id).all()[0]
    if not new:
        return jsonify(errno=RETCODE.PARAMERR, errmsg='该条新闻不存在')
    # 初始化评论模型, 保存数据
    new_comment = Comment()
    new_comment.user_id = user.id
    new_comment.news_id = news_id
    new_comment.content = comment
    new_comment.parent_id = parent_id
    try:
        db.session.add(new_comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    # 返回响应
    return jsonify(errno=RETCODE.OK, errmsg='ok')


@news_blu.route('/comment_like', methods=["POST"])
@user_login_data
def comment_like():
    """
    评论点赞
    Returns:
    """
    # 用户是否登录
    user = g.user
    # 取到请求参数
    data = request.get_json()
    comment_id = data['comment_id']
    action = data['action']
    # 判断参数是否完整
    if not all([comment_id, action]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 获取到要被点赞的评论模型

    commentlike = CommentLike()
    commentlike.comment_id = comment_id
    commentlike.user_id = user.id

    # action的状态,如果点赞,则查询后将用户id和评论id添加到数据库
    # 点赞评论
    if action == 'add':
        db.session.add(commentlike)
        # 更新点赞次数
        comment = Comment.query.get(comment_id)
        count = comment.like_count
        Comment.query.filter_by(id=comment_id).update(
            {'like_count': count + 1})
        db.session.commit()
    else:
        # 取消点赞评论,查询数据库,如果以点在,则删除点赞信息
        CommentLike.query.filter(
            CommentLike.comment_id == comment_id, CommentLike.user_id == user.id).delete()
        # 更新点赞次数
        comment = Comment.query.get(comment_id)
        count = comment.like_count
        Comment.query.filter_by(id=comment_id).update(
            {'like_count': count - 1})
        db.session.commit()
    # 返回结果
    return jsonify(errno=RETCODE.OK, errmsg='ok')


@news_blu.route('/followed_user', methods=["POST"])
@user_login_data
def followed_user():
    """关注或者取消关注用户"""
    # 获取自己登录信息
    user = g.user
    if not user:
        return jsonify(errno=RETCODE.SESSIONERR, errmsg="未登录")

    # 获取参数
    user_id = request.json.get("user_id")
    action = request.json.get("action")

    # 判断参数
    if not all([user_id, action]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg="参数错误")

    if action not in ("follow", "unfollow"):
        return jsonify(errno=RETCODE.PARAMERR, errmsg="参数错误")

    # 获取要被关注的用户
    try:
        other = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RETCODE.DBERR, errmsg="数据查询错误")

    if not other:
        return jsonify(errno=RETCODE.NODATA, errmsg="未查询到数据")

    if other.id == user.id:
        return jsonify(errno=RETCODE.PARAMERR, errmsg="请勿关注自己")

    # 根据要执行的操作去修改对应的数据
    if action == "follow":
        if other not in user.followed:
            # 当前用户的关注列表添加一个值
            user.followed.append(other)
        else:
            return jsonify(errno=RETCODE.DATAEXIST, errmsg="当前用户已被关注")
    else:
        # 取消关注
        if other in user.followed:
            user.followed.remove(other)
        else:
            return jsonify(errno=RETCODE.DATAEXIST, errmsg="当前用户未被关注")

    return jsonify(errno=RETCODE.OK, errmsg="操作成功")

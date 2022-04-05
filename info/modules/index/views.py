"""
index 模块接口
"""

from flask import render_template, request, jsonify, g, current_app
from info import constants
from info.models import News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RETCODE
from . import index_blu


# 首页
@index_blu.route('/')
@user_login_data
def index():
    user = g.user
    news_dict = News.query.order_by(News.clicks.desc()).limit(8).all()
    categories = Category.query.filter().all()
    data = {
        'user': user,
        'news_dict': news_dict,
        'categories': categories
    }
    return render_template('news/index.html', data=data)


@index_blu.route('/news_list')
def news_list():
    """
    获取当前新闻数据
    Returns:
    """
    # 1. 获取参数,并指定默认为"最新"分类,第一页,一页显示10条数据
    page = request.args.get('page')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    cid = request.args.get('cid')
    current_page = 1
    total_page = 1
    news = None

    # 2. 校验参数
    if not all([page, cid]):
        return jsonify(errno=RETCODE.PARAMERR, errmsg='参数不完整')
    # 默认选择最新数据分类
    try:
        if cid == '1' or cid == '0':
            paginate = News.query.filter(News.status == 0).order_by(News.id.desc()).paginate(page,
                                                                                             constants.NEWS_PAGE_MAX_COUNT,
                                                                                             False)
        else:
            paginate = News.query.filter(News.category_id == cid, News.status == 0).paginate(page,
                                                                                             constants.NEWS_PAGE_MAX_COUNT,
                                                                                             False)
        news = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
    # 将模型对象列表转成字典列表
    news_dict_list = []
    for news_item in news:
        news_item = {
            'index_image_url': news_item.index_image_url,
            'title': news_item.title,
            'digest': news_item.digest,
            'source': news_item.source,
            'create_time': news_item.create_time,
            'id': news_item.id
        }
        news_dict_list.append(news_item)
    # 返回数据
    news_data = {
        'total_page': total_page,
        'news_dict_list': news_dict_list,
        "current_page": current_page
    }
    return jsonify(data=news_data)


@index_blu.route('/favicon.ico')
def get_fav():
    return current_app.send_static_file('news/favicon.ico')

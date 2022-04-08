"""
常量文件
"""
IMAGE_CODE_EXPIRES = 60 * 5 # 图片验证码过期时间
SMS_CODE_EXPIRES = 60 * 5 # 短信验证码过期时间
SMS_FLAG_EXPIRES = 60 * 5 # 短信验证码过期标志过期时间

# 图片验证码Redis有效期,  单位：秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码Redis有效期, 单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 七牛空间域名, 开发环境为本地服务链接, 用于拼接图片前缀
QINIU_DOMIN_PREFIX = "http://127.0.0.1:5000"

# 首页展示最多的新闻数量
HOME_PAGE_MAX_NEWS = 10

# 用户的关注每一页最多数量
USER_FOLLOWED_MAX_COUNT = 4

# 用户收藏最多新闻数量
USER_COLLECTION_MAX_NEWS = 10

# 其他用户每一页最多新闻数量
OTHER_NEWS_PAGE_MAX_COUNT = 10
NEWS_PAGE_MAX_COUNT = 10

# 点击排行展示的最多新闻数据
CLICK_RANK_MAX_NEWS = 10

# 管理员页面用户每页多最数据条数
ADMIN_USER_PAGE_MAX_COUNT = 10

# 管理员页面新闻每页多最数据条数
ADMIN_NEWS_PAGE_MAX_COUNT = 10

# 新闻未审核状态
NEWS_NOT_CHECK = 1

# 新闻已审核状态
NEWS_CHECKED = 0

# 接口返回状态码
class RETCODE:
    OK                  = "0"
    DBERR               = "4001"
    NODATA              = "4002"
    DATAEXIST           = "4003"
    DATAERR             = "4004"
    SESSIONERR          = "4101"
    LOGINERR            = "4102"
    PARAMERR            = "4103"
    USERERR             = "4104"
    ROLEERR             = "4105"
    PWDERR              = "4106"
    REQERR              = "4201"
    IPERR               = "4202"
    THIRDERR            = "4301"
    IOERR               = "4302"
    SERVERERR           = "4500"
    UNKOWNERR           = "4501"
    IMAGECODEERR        = "4001"

# 接口返回异常信息
error_map = {
    RETCODE.OK                    : u"成功",
    RETCODE.DBERR                 : u"数据库查询错误",
    RETCODE.NODATA                : u"无数据",
    RETCODE.DATAEXIST             : u"数据已存在",
    RETCODE.DATAERR               : u"数据错误",
    RETCODE.SESSIONERR            : u"用户未登录",
    RETCODE.LOGINERR              : u"用户登录失败",
    RETCODE.PARAMERR              : u"参数错误",
    RETCODE.USERERR               : u"用户不存在或未激活",
    RETCODE.ROLEERR               : u"用户身份错误",
    RETCODE.PWDERR                : u"密码错误",
    RETCODE.REQERR                : u"非法请求或请求次数受限",
    RETCODE.IPERR                 : u"IP受限",
    RETCODE.THIRDERR              : u"第三方系统错误",
    RETCODE.IOERR                 : u"文件读写错误",
    RETCODE.SERVERERR             : u"内部错误",
    RETCODE.UNKOWNERR             : u"未知错误",
}

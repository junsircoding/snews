# coding:utf-8

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
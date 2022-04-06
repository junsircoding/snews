"""
manage.py 是程序启动的入口, 只关心启动的相关参数以及内容
"""
from flask import app
from flask_script import Manager
from flask_migrate import Migrate
# 这个 models 必须导入, flask_migrate 在迁移建表的时候需要
from info import create_app, db, models
from info.models import User


# 通过指定的配置名字创建对应配置的 app
app = create_app('development')
# 将 app 与 db 关联
migrate = Migrate(app, db)
# 命令行管理器
manager = Manager(app)


@manager.option('-n', '-name', dest="name")
@manager.option('-p', '-password', dest="password")
def createsu(name, password):
    """通过命令行创建管理员账号
    """
    if not all([name, password]):
        print("参数不足")
    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)

    print("添加成功")


if __name__ == '__main__':
    manager.run()

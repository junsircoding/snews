"""
manage.py 是程序启动的入口, 只关心启动的相关参数以及内容
"""

from flask_script import Manager
from info import create_app, db
from info.models import User


app = create_app()
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


if __name__ == "__main__":
    manager.run()

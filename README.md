# 新经新闻项目

## 部署项目

1. 安装环境

```shell
pip install -r requirements.txt
```

2. 迁移数据库

```shell
# 设定 Flask App
export FLASK_APP=manage
# 生成迁移文件夹
flask db init
# 生成指定版本迁移文件
flask db migrate -m 'initial'
# 执行迁移
flask db upgrade
```

3. 导入数据

```shell
# 打开 app.db 数据库
sqlite3 info/app.db
.read docs/information_info_category.sql
.read docs/information_info_news.sql
```

4. 启动 Redis

```shell
redis-server
```

5. 创建管理员账户

```shell
python manage.py createsu -n admin -p 123456
```

6. 填写自己项目的 SECRET_KEY, 位于 `config.py` 中.

7. 运行项目

```shell
python manage.py runserver
```

## 运行效果

![](./docs/img/index.png)
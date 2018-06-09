# _*_ coding:utf-8 _*_

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models  # 导入models只是为了迁移时manage可以找到
from info.models import User


app = create_app('dev')
# 创建迁移对象
manager = Manager(app)
# 将app与db关联
Migrate(app, db)
# 迁移命令加入命令管理
manager.add_command('mysql', MigrateCommand)


@manager.option('-u', '-username', dest='username')
@manager.option('-p', '-password', dest='password')
@manager.option('-m', '-mobile', dest='mobile')
def createsuperuser(username, password, mobile):
    """创建超级管理员的脚本函数"""
    if not all([username, password, mobile]):
        print('缺少必要的参数')
    else:
        user = User()
        user.nick_name = username
        user.password = password
        user.mobile = mobile
        # 关键点
        user.is_admin = True
        try:
            db.session.add(user)
            db.session.commit()
            print('创建成功!')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    print(app.url_map)
    manager.run()

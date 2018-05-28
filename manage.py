# _*_ coding:utf-8 _*_

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models

app = create_app('dev')
# 创建迁移对象
manager = Manager(app)
# 将app与db关联
Migrate(app, db)
# 迁移命令加入命令管理
manager.add_command('mysql', MigrateCommand)


if __name__ == '__main__':
    print(app.url_map)
    manager.run()

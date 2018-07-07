#! /usr/bin/env python

"""
思路：
1. django进行初始化
2. 执行生成静态化的首页
"""

"""
功能：手动生成index.html首页静态文件
使用方法:
    ./regenerate_index_html.py
"""
import sys
# 有可能执行这个文件的时候，django项目并没有启动,所以需要重新添加导包路径
sys.path.insert(0, '../')  # meiduo_mall/meiduo_mall/
sys.path.insert(0, '../meiduo_mall/apps')  # meiduo_mall/meiduo_mall/meiduo_mall/apps

import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 让django进行初始化设置[因为我们当前的生成首页的时候需要读取数据库，所以需要让django先连接数据库]
import django

django.setup()

from contents.crons import generate_static_index_html

if __name__ == '__main__':
    generate_static_index_html()

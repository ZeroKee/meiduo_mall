# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-6 下午3:15
from collections import OrderedDict

from .models import GoodsChannel

def get_categories():
    """
    获取商品分类菜单
    :return: 菜单字典
    """
    # 获取菜单字典
    """
    categories = {
         1: { # 组1
             'channels': [{'id':, 'name':, 'url':},{}, {}...],  # 频道
             'sub_cats': [{'id':, 'name':, 'sub_cats':[{},{}]}, {}, {}, ..]  # 子类
         },
         2: { # 组2

         }
     }
    """
    categories = OrderedDict()
    # 拿到所有的频道，并按组和组内顺序来排名
    channels = GoodsChannel.objects.order_by('group_id','sequence')
    for channel in channels:
        group_id = channel.group_id

        # 如果当前组还没有构建表结构，就构建一下表结构
        if group_id not in categories.keys():
            categories[group_id] = {'channels':[], 'sub_cats':[]}

        # 当前频道的类别
        cat1 = channel.category

        # 有表结构就直接将对应的数据放到categories中
        categories[group_id]['channels'].append({
            'id':cat1.id,
            'name':cat1.name,
            'url':channel.url
        })

        # 通过自关联拿到当前频道的所有分类的分类
        for cat2 in cat1.goodscategory_set.all():
            cat2.sub_cats = []  # 二级分类列表
            for cat3 in cat2.goodscategory_set.all():
                cat2.sub_cats.append(cat3)  # 三级分类列表
            categories[group_id]['sub_cats'].append(cat2)

        return categories

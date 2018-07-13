# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-6 下午3:06
from celery_tasks.main import app
from django.template import loader
from django.conf import settings
import os

from goods.models import SKU
from goods.utils import get_categories


@app.tasks(name='generate_static_sku_detail_html')
def generate_static_sku_detail_html(sku_id):
    """
    供运营人员，在修改商品详细信息后，生成静态商品详情页
    :param sku_id: 商品id
    :return: 静态详情页
    """
    # 获取商品分类菜单
    categories = get_categories()

    # 获取当前sku的信息，对象和通过外键关联获取所有的图片
    sku = SKU.objects.get(id=sku_id)
    sku.images = sku.skuimage_set.all()  # 一对多查询子模型时的语法就是.all(),等同与objects.all()

    # 面包屑导航信息中的频道
    goods = sku.goods
    goods.channel = goods.category1.goodscategory_set.all()[0]
    # 生成当前商品的具体规格
    sku_specs = sku.skuspecification_set.all()
    sku_key = []
    # skuspecification表中储存有spu的规格名和option规格值
    for spec in sku_specs:
        sku_key.append(spec.option.id)
    # 获取当前商品的所有sku
    skus = goods.sku_set.all()

    # 构建不同规格参数（选项）的sku字典
    # spec_sku_map = {
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     (规格1参数id, 规格2参数id, 规格3参数id, ...): sku_id,
    #     ...
    # }
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.skuspecification_set.order_by('spec_id')  # 在多的一方保存的字段是类名_id:spec_id
        # 用于形成规格参数-sku字典里的键
        key=[]
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    # 获取当前商品的规格信息
    specs = goods.goodsspecification_set.order_by('id')  # 上面也是通过goodsspecification中的id来排序的，以此来实现规格和商品详细信息的一一对应

    # 如果当前sku的规格信息不完整，则不再继续
    if len(sku_key)< len(specs):
        return
    for index, spec in enumerate(specs):  # specs是一个列表
        key = sku_key[:]
        options = spec.specificationoption_set.all()
        for option in options:
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))

        spec.options = options

    # 渲染模板生成静态html页面
    context = {
        'categories':categories,
        'goods':goods,
        'specs':specs,
        'sku':sku
    }

    # 获取详情页模板
    template = loader.get_template('detail.html')
    # 传如数据，替换模板相应的值
    html_text = template.render(context)
    # 生成根据商品id生成html文件并保存在goods静态文件目录中
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'goods/'+str(sku_id)+'.html')
    with open(file_path, 'w') as f:
        f.write(html_text)

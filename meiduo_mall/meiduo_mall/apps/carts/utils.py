# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-7 下午9:17
from django_redis import get_redis_connection

import pickle, base64

def merge_cart_cookie_to_redis(request, user, response):
    """
    登陆合并cookie中的数据到redis中
    :param request: 从中获取cookie_cart
    :param user: 获取user.id
    :param response: 用于删除cookie
    :return: response
    """

    cookie_cart = request.COOKIES.get('cart')

    if cookie_cart is not None:
        cookie_cart = pickle.loads(base64.b64decode(cookie_cart.encode()))
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

        # 为了将所有的redis操作都放到一起，减少操作次数，
        # 我们将redis_cart中的所有数据拿出来，修改之后再一次性修改
        cart = {}  # 用于存放sku_id与count对应关系的字典

        for sku_id, count in redis_cart.items():
            cart[int(sku_id)] = int(count)

        for sku_id, count_selected_dict in cookie_cart:
            cart[int(sku_id)] = count_selected_dict.get('count')
            if count_selected_dict.get('selected'):
                redis_cart_selected.add(sku_id)

        if cart:
            pl = redis_conn.pipeline()
            # hmset 向hash中添加多个值
            pl.hmset('cart_%s' % user.id, cart)
            # sadd
            pl.sadd('cart_selected_%s' % user.id, *redis_cart_selected)
            pl.execute()

        # 删除指定cookie
        response.delete_cookie('cart')

    return response





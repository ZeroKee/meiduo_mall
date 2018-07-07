from rest_framework.views import APIView
from rest_framework.response import Response
from django_redis import get_redis_connection
from rest_framework import status

import pickle, base64

from .serializers import CartSerializer, CartSKUSerializer
from goods.models import SKU


class CartView(APIView):
    # 关闭登录认证
    def perform_authentication(self, request):
        # 重写执行认证函数
        # 原本该函数写的是 request.user  即用户未登录会直接返回401
        # 因为允许用户在未登录的情况下加入购物车,重写该函数后，手动判断request.user是否为None来区分用户的登陆状态
        pass

    def post(self, request):
        """
        添加商品到购物车
        :param request:
        :return: 购物车信息sku_id, count, selected
        """
        # 使用序列化器验证购物车数据
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected')

        # 尝试冲request.user中获取user
        try:
            user = request.user
        except Exception:
            user = None

        # 用户已登陆， 将购物车信息存储在redis中
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            # 类似与mysql的事务
            pl = redis_conn.pipeline()
            # 用hash储存数量，hincrby 没有就新增，有就增加（并不是覆盖）
            # 存储格式：{user.id:{sku_id:count,sku_id:count}}
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # set储存勾选状态, sadd 会进行值去重
            # 存储格式：{user.id:{sku_id, sku_id, sku_id}}
            pl.sadd('cart_selected_%s' % user.id, sku_id)

            pl.execute()
            return Response(data)
        else:
            # {
            #     1001: { "count": 10, "selected": True},
            #     ...
            # }
            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            # 未登陆则从cookie中拿到原有的购物车数据，然后修改cookie再set_cookie
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
            # 这里的sku指的是字典里面的键sku_id，为了避免与上面同名所以取名sku
            sku = cart.get(sku_id)
            if sku:
                count += int(sku.get('count'))
            cart[sku_id] = {
                'count': count,
                'selected': True
            }
            response = Response(data=serializer.data)
            response.set_cookie('cart', base64.b64encode(pickle.dumps(cart)).decode())
            return response

    def get(self, request):
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # hgetall 获取所有域和值， hget获取指定域的值
            redis_cart = pl.hgetall('cart_%s' % user.id)
            # smembers 获取集合类的所有值，没有返回空集合
            redis_selected = pl.smembers('cart_selected_%s' % user.id)

            cart = {}
            for key, value in redis_cart.items():
                cart[key] = {
                    'count': int(value),
                    'selected': True if key in redis_selected else False
                }
        else:
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
        # 获取要进行序列化操作的对象
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        serializer = CartSKUSerializer(skus, many=True)  # 对多个对象进行序列化操作时需要指定many=True
        return Response(serializer.data)

    def put(self, request):
        # 使用序列化器验证购物车数据
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected')

        # 尝试冲request.user中获取user
        try:
            user = request.user
        except Exception:
            user = None

        # 用户已登陆， 将购物车信息存储在redis中
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            # 类似与mysql的事务
            pl = redis_conn.pipeline()
            # 用hash储存数量，hset 对应的域有值，则覆盖
            # 存储格式：{user.id:{sku_id:count,sku_id:count}}
            pl.hset('cart_%s' % user.id, sku_id, count)
            if selected:
                # set储存勾选状态, sadd 会进行值去重
                # 存储格式：{user.id:{sku_id, sku_id, sku_id}}
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                # 移除集合中的一个或者多个值，如果值不存在则跳过
                pl.srem('cart_selected_%s' % user.id, sku_id)

            pl.execute()
            return Response(data)
        else:
            # {
            #     1001: { "count": 10, "selected": True},
            #     ...
            # }
            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            # 未登陆则从cookie中拿到原有的购物车数据，然后修改cookie再set_cookie
            cart = request.COOKIES.get('cart')
            if cart is not None:
                cart = pickle.loads(base64.b64decode(cart.encode()))
            else:
                cart = {}
            # 这里的sku指的是字典里面的键sku_id，为了避免与上面同名所以取名sku
            sku = cart.get(sku_id)
            if sku:
                count += int(sku.get('count'))
            cart[sku_id] = {
                'count': count,
                'selected': True
            }
            response = Response(data=serializer.data)
            response.set_cookie('cart', base64.b64encode(pickle.dumps(cart)).decode())
            return response

    def delete(self, request):
        sku_id = request.data.get('sku_id')

        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # hdel 删除指定域的数据， 不存在会忽略
            pl.hdel('cart_%s' % user.id, sku_id)
            # srem 删除指定值
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()

        else:
            response = Response(status=status.HTTP_204_NO_CONTENT)

            cart = request.COOKIES.get('cart')
            cart = pickle.loads(base64.b64decode(cart.encode()))
            if cart is None:
                return response
            else:
                if sku_id in cart:
                    del cart[sku_id]
                    response.set_cookie('cart', base64.b64encode(pickle.dumps(cart)).decode())
            return response



from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from contents.models import ContentCategory
from contents.utils import get_categories
from coupons.models import CouponInfo, CouponComb, CouponDetail
from coupons.utils import skus_with_coupon
from meiduo_mall.utils.response_code import RETCODE


class CouponShowView(View):
    """优惠券领取基本页面"""

    def get(self, request):
        # 获取3级商品分类
        categories = get_categories()

        contents = {}
        content_classify = ContentCategory.objects.all()  # 获取广告类别
        for cat in content_classify:
            # sequence 字段是同类别广告内顺序
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 渲染模板的上下文
        context = {
            "categories": categories,  # 商品分类列表
            "contents": contents,  # 各种商品广告(轮播图，快讯等等)
        }

        return render(request, "coupon_get.html", context)


class CouponInfoView(View):
    """通过js获取可领优惠券信息"""

    def get(self, request):
        """请求具体优惠券信息"""

        user = request.user
        # 显示所有公开可领取的
        coupon_all = CouponInfo.objects.filter(receive=True, security_level=0)

        coupon_info = []
        for coupon in coupon_all:

            # expiry_date:有效期：str ,先判断有效期问题，过了有效期就不需要判断下面了
            if coupon.end_date < timezone.now().date():  # 获取现在日期 timezone.now()是datetime ,要转date格式来比较
                coupon.receive = False  # 如果优惠券已经过期，把可领状态关闭掉
                coupon.save()
                continue  # 继续检查下一张

            # 没有过期执行下面，返回拼接的有效期 # 组合的日期要改 2019.06.30-2019.09.21
            # expiry_date = str(coupon.start_date) + "-" + str(coupon.end_date)

            expiry_date = coupon.start_date.strftime('%Y.%m.%d') + "-" + coupon.end_date.strftime('%Y.%m.%d')

            coupon_rules = coupon.type.rules.all()

            if coupon.type_id == 3:
                discount = "兑换券"  # 类型3为兑换券，数据库没有discount值
                color = 3
            else:
                # discount:满减金额 折扣 或者 兑换券 str
                coupon_discount = coupon_rules.get(key="discount")
                discount = CouponComb.objects.get(coupon=coupon, rule=coupon_discount).option.value
                if coupon.type_id == 1:  # 满减的类型
                    color = 0 if float(discount) > 30 else 1  # 0-黄色 1-绿色
                    discount = "￥%.2f" % float(discount)
                else:
                    discount = "%s 折" % discount  # ==2 折扣类型 组合 8.5 折 这样
                    color = 2

            # threshold:使用条件，如满多少可用 无门槛等 str
            coupon_threshold = coupon_rules.get(key="threshold")
            threshold = CouponComb.objects.get(coupon=coupon, rule=coupon_threshold).option.value
            if threshold == "0":
                threshold = "无门槛"
            else:
                threshold = f"满{threshold}可用"

            # status:是否可以领取-True为显示 # 查这张券的数量
            if user.is_authenticated:  # 没有登录，直接False
                user_count = CouponDetail.objects.filter(user=user, coupon=coupon).count()
                if coupon.limit == 0 or user_count < coupon.limit:
                    status = True
                else:
                    status = False
            else:
                status = True

            # select.url:点击展现范围 url 后面再考虑接口问题
            select_url = f"/coupon/select/{coupon.id}/1/"

            coupon_info.append({
                "id": str(coupon.id),
                "discount": discount,
                "threshold": threshold,
                "select": coupon.select_str,
                "select_url": select_url,
                "expiry_date": expiry_date,
                "status": str(status),  # 转字符串方便点
                "color": color  # 黄绿红蓝 0-3
            })

        return JsonResponse({"code": RETCODE.OK, "errmsg": "ok", "coupon_info": coupon_info})


class CouponGetView(View):
    """领取优惠券"""

    def get(self, request, coupon_id):
        print("领取优惠券", coupon_id)

        if not request.user.is_authenticated:
            return JsonResponse({"code": RETCODE.SESSIONERR, "errmsg": "请登录后再领取"})

        try:
            coupon = CouponInfo.objects.get(id=coupon_id, security_level=0)
        except CouponInfo.DoesNotExist:
            return JsonResponse({"code": RETCODE.DBERR, "errmsg": "优惠券不存在"})

        if coupon.receive == False:
            return JsonResponse({"code": RETCODE.DBERR, "errmsg": "优惠券失效"})

        if coupon.end_date < timezone.now().date():
            coupon.receive = False
            coupon.save()
            return JsonResponse({"code": RETCODE.DBERR, "errmsg": "优惠券失效"})

        user = request.user
        user_count = CouponDetail.objects.filter(user=user, coupon=coupon).count()
        if coupon.limit != 0 and user_count >= coupon.limit:
            return JsonResponse({"code": RETCODE.DBERR, "errmsg": "领取已达上限"})

        CouponDetail.objects.create(user=user, coupon=coupon)
        user_count = CouponDetail.objects.filter(user=user, coupon=coupon).count()
        if user_count >= coupon.limit:
            return JsonResponse({"code": RETCODE.OK, "errmsg": "领取成功", "new_status": "False"})
        else:
            return JsonResponse({"code": RETCODE.OK, "errmsg": "领取成功", "new_status": "True"})


class CouponSelectView(View):
    """优惠券范围"""

    def get(self, request, coupon_id, page_num):
        try:
            coupon = CouponInfo.objects.get(id=coupon_id)
        except CouponInfo.DoesNotExist:
            return render(request, "coupon_select.html", {"errmsg": "有问题"})

        if coupon.status == False:
            return render(request, "coupon_select.html", {"errmsg": "优惠券已失效"})

        # 看前端传来的排序，进行识别
        sort = request.GET.get("sort", "default")
        sort_now = request.GET.get("sort_now", "default")
        if sort == "price":
            sort_field = "-price" if sort_now == "price" else "price"
        elif sort == "hot":
            sort_field = "sales" if sort_now == "-sales" else "-sales"
        else:
            sort = "default"  # 如果不按价格和热度，那全部改默认
            sort_field = "create_time"

        skus = skus_with_coupon(coupon)  # 自己封装的获取全部skus

        skus = skus.order_by(sort_field)  # 重新排序
        hots = skus.order_by("-sales")[:2]

        paginator = Paginator(skus, 5)  # 分页器
        try:
            page_skus = paginator.page(page_num)
        except Exception as e:
            print(e)
            return HttpResponseNotFound("empty page")
        total_page = paginator.num_pages
        page_num = page_num

        context = {
            'categories': get_categories(),  # 频道分类
            'breadcrumb': coupon.select_str,  # 面包屑导航 >>> 改优惠券名称 或者限购范围描述
            'sort': sort,  # 排序字段
            'sort_now': sort_field,
            'coupon_id': coupon_id,
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
            "hots": hots,  # 本优惠券热销的部分
        }

        return render(request, "coupon_select.html", context)


class CouponShowByCenterView(View):
    """用户中心展示优惠券"""

    def get(self, request):
        user = request.user
        # 显示所有公开可领取的
        coupon_detail_all = CouponDetail.objects.filter(user=user)
        coupon_start = []
        coupon_end = []
        for x in coupon_detail_all:
            coupon = x.coupon

            # expiry_date:有效期：str ,先判断有效期问题，过了有效期就不需要判断下面了
            if coupon.end_date < timezone.now().date():  # 获取现在日期 timezone.now()是datetime ,要转date格式来比较
                coupon.receive = False  # 如果优惠券已经过期，把可领状态关闭掉
                coupon.save()
                continue  # 继续检查下一张

            # 没有过期执行下面，返回拼接的有效期 # 组合的日期要改 2019.06.30-2019.09.21
            # expiry_date = str(coupon.start_date) + "-" + str(coupon.end_date)

            expiry_date = coupon.start_date.strftime('%Y.%m.%d') + "-" + coupon.end_date.strftime('%Y.%m.%d')

            coupon_rules = coupon.type.rules.all()

            if coupon.type_id == 3:
                discount = "兑换券"  # 类型3为兑换券，数据库没有discount值
                color = 3
            else:
                # discount:满减金额 折扣 或者 兑换券 str
                coupon_discount = coupon_rules.get(key="discount")
                discount = CouponComb.objects.get(coupon=coupon, rule=coupon_discount).option.value
                if coupon.type_id == 1:  # 满减的类型
                    color = 0 if float(discount) > 30 else 1  # 0-黄色 1-绿色
                    discount = "￥%.2f" % float(discount)
                else:
                    discount = "%s 折" % discount  # ==2 折扣类型 组合 8.5 折 这样
                    color = 2

            # threshold:使用条件，如满多少可用 无门槛等 str
            coupon_threshold = coupon_rules.get(key="threshold")
            threshold = CouponComb.objects.get(coupon=coupon, rule=coupon_threshold).option.value
            if threshold == "0":
                threshold = "无门槛"
            else:
                threshold = f"满{threshold}可用"

            # status:True 已经使用  # 查这张券的数量
            if x.order:
                status = True
            else:
                status = False

            # select.url:点击展现范围 url 后面再考虑接口问题
            select_url = f"/coupon/select/{coupon.id}/1/"

            temp = {
                "id": str(coupon.id),
                "discount": discount,
                "threshold": threshold,
                "select": coupon.select_str,
                "select_url": select_url,
                "expiry_date": expiry_date,
                "status": str(status),  # 转字符串方便点
                "color": color  # 黄绿红蓝 0-3
            }
            if x.order:
                coupon_end.append(temp)
            else:
                coupon_start.append(temp)

        coupon_info = coupon_start + coupon_end
        print("用户中心 优惠券信息=", coupon_info)

        return JsonResponse({"code": RETCODE.OK, "errmsg": "ok", "coupon_info": coupon_info})


class CouponGodView(LoginRequiredMixin, View):
    """上帝模式"""

    def get(self, request):
        print("上帝模式")

        categories = get_categories()

        contents = {}
        content_classify = ContentCategory.objects.all()  # 获取广告类别
        for cat in content_classify:
            # sequence 字段是同类别广告内顺序
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        god_url = "http://www.meiduo.site:8000/god/" + str(request.user.id) + "/"
        context = {
            "categories": categories,  # 商品分类列表
            "contents": contents,  # 各种商品广告(轮播图，快讯等等)
            "god_url": god_url,  # 上帝链接
        }

        return render(request, "coupon_god.html", context)


class GodView(View):
    """上帝模式"""

    def get(self, request, user_id):
        print("通过上帝模式来客户了")

        user = request.user
        response = redirect("/")
        if user.is_authenticated:
            response.delete_cookie("god")
            return response

        response.set_cookie("god", user_id)
        return response

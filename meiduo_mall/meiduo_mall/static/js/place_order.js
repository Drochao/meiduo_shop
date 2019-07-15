Vue.filter('money', function(val) {
    val = val.toString().replace(/\$|\,/g,'');
    if(isNaN(val)) {
      val = "0";
    }
    let sign = (val == (val = Math.abs(val)));
    val = Math.floor(val*100+0.50000000001);
    let cents = val%100;
    val = Math.floor(val/100).toString();
    if(cents<10) {
       cents = "0" + cents
    }
    for (var i = 0; i < Math.floor((val.length-(1+i))/3); i++) {
        // val = val.substring(0,val.length-(4*i+3))+',' + val.substring(val.length-(4*i+3));
        // 下面这行不要 逗号 分割
        val = val.substring(0,val.length-(4*i+3)) + val.substring(val.length-(4*i+3));
    }

    return (((sign)?'':'-') + val + '.' + cents);
});

var vm = new Vue({
    el: '#app',
	// 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host: host,
        order_submitting: false, // 正在提交订单标志
        pay_method: 2, // 支付方式,默认支付宝支付
        nowsite: '', // 默认地址
        nowcoupon: '', // 选择的优惠券
        payment_amount: '',
        discounts:"",   // 折扣
        coupons:coupons,
        pay_original:pay_original,
    },
    mounted(){
        // 初始化
        this.payment_amount = payment_amount;
        // 绑定默认地址
        this.nowsite = default_address_id;
        // 绑定默认优惠券
        this.nowcoupon = default_coupon_id;
        if (this.nowcoupon != "0"){this.change_coupon(this.nowcoupon,1);};

    },
    methods: {
        change_coupon(coupon_id, index){
            console.log(coupon_id, index);
            this.nowcoupon = coupon_id;
            this.discounts = coupons[index];
            this.payment_amount = pay_original - this.discounts;
        },

        // 提交订单
        on_order_submit(){
            if (!this.nowsite) {
                alert('请补充收货地址');
                return;
            }
            if (!this.pay_method) {
                alert('请选择付款方式');
                return;
            }
            if (this.order_submitting == false){
                this.order_submitting = true;
                var url = this.host + '/orders/commit/';
                axios.post(url, {
                        address_id: this.nowsite,
                        pay_method: parseInt(this.pay_method),
                        coupon_id: this.nowcoupon,
                    }, {
                        headers:{
                            'X-CSRFToken':getCookie('csrftoken')
                        },
                        responseType: 'json'
                    })
                    .then(response => {
                        if (response.data.code == '0') {
                            location.href = '/orders/success/?order_id='+response.data.order_id
                                        +'&payment_amount='+this.payment_amount
                                        +'&pay_method='+this.pay_method;
                        } else if (response.data.code == '4101') {
                            location.href = '/login/?next=/orders/settlement/';
                        } else {
                            alert(response.data.errmsg);
                        }
                    })
                    .catch(error => {
                        this.order_submitting = false;
                        console.log(error.response);
                    })
            }
        }
    }
});

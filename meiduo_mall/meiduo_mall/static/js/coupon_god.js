var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host,
        cart_total_count: 0, // 购物车总数量
        carts: [], // 购物车数据,
        username: '',
        coupons: "",
        // 黄绿红蓝 0-3
        color: [
            "coupon coupon-wave-left coupon-wave-right coupon-yellow-gradient",
            "coupon coupon-wave-left coupon-wave-right coupon-green-gradient",
            "coupon coupon-wave-left coupon-wave-right coupon-red-gradient",
            "coupon coupon-wave-left coupon-wave-right coupon-blue-gradient"
        ]
    },

    mounted() {
        // 获取购物车数据
        this.get_coupons();
        this.get_carts();
        this.username = getCookie('username');
    },
    methods: {


        // 获取购物车数据
        get_carts() {
            var url = this.host + '/carts/simple/';
            axios.get(url, {
                responseType: 'json',
            })
                .then(response => {
                    this.carts = response.data.cart_skus;
                    this.cart_total_count = 0;
                    for (var i = 0; i < this.carts.length; i++) {
                        if (this.carts[i].name.length > 25) {
                            this.carts[i].name = this.carts[i].name.substring(0, 25) + '...';
                        }
                        this.cart_total_count += this.carts[i].count;
                    }
                })
                .catch(error => {
                    console.log("出了点小问题");
                })
        },

        get_coupons() {
            var url = this.host + '/coupon/all/';
            axios.get(url, {
                responseType: 'json',
            })
                .then(response => {
                    this.coupons = JSON.parse(JSON.stringify(response.data.coupon_info));
                })
                .catch(error => {
                    console.log(error.response);
                })
        },

        receive_a_coupon(id, index) {
            var url = this.host + '/coupon/get/' + id + '/';

            axios.get(url, {
                responseType: 'json',
            })
                .then(response => {
                    if (response.data.code == '0') {
                        Vue.set(this.coupons[index], "status", response.data.new_status);
                        alert("领取成功");

                    } else if (response.data.code == '4101') {
                        alert(response.data.errmsg);
                        location.href = '/login/?next=/coupon/';
                    }
                    else {
                        console.log("恩。。。？");
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log("发送失败？");
                    // console.log(error.response);
                })
        },


    }
});

var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host,
        sku_count: 1,
        cart_total_count: 0, // 购物车总数量
        carts: [], // 购物车数据,
        username: '',

    },
    mounted(){
        // 获取购物车数据
        this.get_carts();

        this.username = getCookie('username');
    },
    methods: {
        // 加入购物车
        add_cart(id){
            var url = this.host + '/carts/';
            axios.post(url, {
                    sku_id: parseInt(id),
                    count: this.sku_count
                }, {
                    headers: {
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json',
                    withCredentials: true
                })
                .then(response => {
                    if (response.data.code == '0') {
                        alert('添加购物车成功');
                        this.cart_total_count += this.sku_count;
                        this.get_carts();
                    } else { // 参数错误
                        alert(response.data.errmsg);
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
        // 获取购物车数据
        get_carts(){
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
                    console.log(error.response);
                })
        },
    }
});
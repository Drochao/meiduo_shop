var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host,
        f1_tab: 1, // 1F 标签页控制
        f2_tab: 1, // 2F 标签页控制
        f3_tab: 1, // 3F 标签页控制
        cart_total_count: 0, // 购物车总数量
        carts: [], // 购物车数据,
        username:'',
        city_weather1:"",
        city_weather2:"",
        weather_png:"",
    },
    mounted(){
        // 获取购物车数据
        this.get_carts();
        this.username=getCookie('username');
        console.log(this.username);
        this.city_weather();
    },
    methods: {
        // 获取购物车数据
        get_carts(){
            var url = this.host+'/carts/simple/';
            axios.get(url, {
                    responseType: 'json',
                })
                .then(response => {
                    this.carts = response.data.cart_skus;
                    this.cart_total_count = 0;
                    for(var i=0;i<this.carts.length;i++){
                        if (this.carts[i].name.length>25){
                            this.carts[i].name = this.carts[i].name.substring(0, 25) + '...';
                        }
                        this.cart_total_count += this.carts[i].count;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
        city_weather(){
            var url = "https://www.tianqiapi.com/api/";
            axios.get(url, {
                    responseType: 'json',
                })
                .then(response => {
            // console.log(response);
                    this.city_weather1 = response.data;
                    this.get_weather_date();
                })
                .catch(error => {
                    console.log(error.response);
                });
                 return this.city_weather1;
        },
        get_weather_date(){
            // console.log(this.city_weather1);
            var url = this.host+'/weather/';
            axios.post(url,
                {
                    all_weather_date: this.city_weather1
                },
                {
                    headers: {
                        'X-CSRFToken':getCookie('csrftoken')
                    },
                    responseType: 'json',
                })
                .then(response => {
                    this.city_weather2 = response.data.weather;
                    this.weather_png = "/static/images/apple/" + this.city_weather2[0] + ".png";
                    // console.log(this.city_weather2[2]);
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
    }
});

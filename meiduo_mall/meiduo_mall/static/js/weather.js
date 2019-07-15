$(function () {
    // 加载完成上升高度完全显示 188  animate() 方法执行 CSS 属性集的自定义动画
    $('.ad').animate({height: 288});
    setInterval(f1, 5000);

    function f1() {
        $(function () {
            $('.ad').animate({height: 0}, 2000);
        });
    };

    // 鼠标点击事件执行回退
    $('.close_btn').click(function () {
        $(this).parent().animate({height: 0});
    });
});
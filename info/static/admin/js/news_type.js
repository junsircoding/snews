$(function () {
    var c_id = null;
    //打开添加分类框
    $('.addtype').click(function () {
        $('.pop_con').show();
    });

    //打开修改分类框
    $('.edit').click(function () {
        c_id = $(this).attr('data-cid');
        $('.pop_con').show();
    });

    // 关闭修改或添加分类框
    $('.cancel').click(function () {
        $('.pop_con').hide();
    });


    $(".pop_con").submit(function (e) {
        e.preventDefault();
        var c_name = $(".input_txt3").val();
        var params = {
            "c_name": c_name,
            "id": c_id
        };
        // 发起修改分类请求
        $.ajax({
            url: "/admin/news_type",
            method: "post",
            headers: {
                // "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            contentType: "application/json",
            success: function (resp) {
                if (resp.errno == "0") {
                    // 刷新当前界面
                    location.reload();
                } else {
                    $error.html(resp.errmsg).show();
                }
            }
        })
    });


});
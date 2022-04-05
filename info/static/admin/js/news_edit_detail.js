$(function () {
    $(".news_edit").submit(function (e) {
        e.preventDefault();
        $(this).ajaxSubmit({
            beforeSubmit: function (request) {
                // 在提交之前, 对参数进行处理
                for (var i = 0; i < request.length; i++) {
                    var item = request[i]
                    if (item["name"] == "content") {
                        item["value"] = tinyMCE.activeEditor.getContent()
                    }
                }
            },
            url: "/admin/news_edit_detail",
            type: "POST",
            headers: {
                // "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    // 返回上一页, 刷新数据
                    location.href = document.referrer;
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    })
});

function cancel() {
    window.location.href = "news_edit";
}

$(".news_filter_form").submit(function (e) {
    e.preventDefault();
    var keyword = $(".input_txt").val();
    var params = {
        "keywords":keyword
    };
    $.ajax({
        url:"/admin/news_edit",
        method:"post",
        headers:{},
        data:JSON.stringify(params),
        contentType:"application/json",
        success:function (resp) {
            if(resp.errno == "0"){
                //刷新当前页面
                location.reload();
            }else{
                $error.html(resp.errmsg).show();
            }
        }
    })
});
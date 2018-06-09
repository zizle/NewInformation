function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {
 // TODO 发布完毕之后需要选中我的发布新闻
    $(".release_form").submit(function (e) {
        e.preventDefault()

        $(this).ajaxSubmit({
            // 读取富文本编辑器里面的文本信息
            beforeSubmit: function (request) {
                // 在提交之前，对参数进行处理
                for (var i = 0; i < request.length; i++) {
                    var item = request[i];
                    if (item["name"] == "content") {
                        item["value"] = tinyMCE.activeEditor.getContent()
                    }
                }
            },
            url:'/user/release_news',
            type:'post',
            headers:{'X-CSRFToken': getCookie('csrf_token')},
            success:function (response) {
                if (response.errno=='0'){
                    alert(response.errmsg);
                    // 选中索引为6的左边单菜单
                    window.parent.fnChangeMenu(6);
                    // 滚动到顶部
                    window.parent.scrollTo(0, 0)
                }else{alert(response.errmsg)}
            }
        })
    })
});
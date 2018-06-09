function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function(){

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // TODO 收藏
    $(".collection").click(function () {
        $.ajax({
            url: '/news/collected',
            type: 'post',
            data: JSON.stringify({'news_id': $(this).attr('data-newid')}),
            contentType: 'application/json',
            headers: {'X-CSRFToken': getCookie('csrf_token')}
        })
            .done(function (response) {
                if (response.errno == '0'){
                    alert(response.errmsg)
                    $('.collection').hide();
                    $('.collected').show();
                }
                else if (response.errno == '4101'){
                    $('.login_form_con').show();
                }else {
                    alert(response.errmsg)
                }
            })
            .fail(function () {
                alert('服务器超时，请重试！')
            })
    });
    // TODO 取消收藏
    $(".collected").click(function () {
        $.ajax({
            url: '/news/cancel_collected',
            type: 'post',
            data: JSON.stringify({'news_id': $(this).attr('data-newid')}),
            contentType: 'application/json',
            headers: {'X-CSRFToken': getCookie('csrf_token')}
        })
            .done(function (response) {
                if (response.errno == '0'){
                    alert(response.errmsg);
                    // 隐藏已收藏按钮
                    $('.collected').hide();
                    // 显示收藏按钮
                    $('.collection').show();
                }
            })
            .fail(function () {
                alert('服务器超时，请重试!')
            })
    });

    // TODO 评论新闻
    $(".comment_form").submit(function (e) {
        e.preventDefault();
        var params = {
            'comment_content': $('.comment_input').val(),
            'news_id': $(this).attr('data-newsid')
        };
        $.ajax({
            url:'/news/comment_news',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken': getCookie('csrf_token')}
        })
            .done(function (response) {
                if (response.errno == '4101'){
                    $('.login_form_con').show()
                }
                else if (response.errno == '0'){
                    alert(response.errmsg);
                    // 接收响应数据
                    var comment_user = response.data.comment.user;
                    var comment = response.data.comment;
                    // 拼接评论内容html
                    var comment_html = '';
                    comment_html += '<div class="comment_list">';
                    comment_html += '<div class="person_pic fl">';
                    comment_html += '<img src="';
                        if (comment_user.avatar_url){comment_html += comment_user.avatar_url}
                        else{comment_html += '../../static/news/images/cat.jpg'}
                    comment_html += '" alt="用户图标"></div>';
                    comment_html += '<div class="user_name fl">';
                    comment_html += comment_user.nick_name;
                    comment_html += '</div>';
                    comment_html += '<div class="comment_text fl">';
                    comment_html += comment.content;
                    comment_html += '</div>';
                    comment_html += '<div class="comment_time fl">';
                    comment_html += comment.create_time;
                    comment_html += '</div>';
                    comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="'+comment.id+'">' + '赞</a>';
                    comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>';
                    comment_html += '<from class="reply_form fl" data-newsid="'+comment.news_id+'" data-commentid="'+comment.id+'">';
                    comment_html += '<textarea class="reply_input"></textarea>';
                    comment_html += '<input type="submit" name="" value="回复" class="reply_sub fr">';
                    comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                    comment_html += '</from></div>';
                    // 追加在当前所有评论的前面，动态更新
                    $('.comment_list_con').prepend(comment_html);
                    // 输入框失去焦点
                    $('.comment_sub').blur();
                    // 清空输入框内容
                    $('.comment_input').val('');
                }
                else{alert(response.errmsg)}
            })
            .fail(function () {
                alert('服务器超时，请重试!')
            })
    });
        // TODO 点赞
    $('.comment_list_con').delegate('a,input','click',function() {

        var sHandler = $(this).prop('class');

        if (sHandler.indexOf('comment_reply') >= 0) {
            $(this).next().toggle();
        }

        if (sHandler.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle();
        }

        if (sHandler.indexOf('comment_up') >= 0) {
            var $this = $(this);
            // 表示当前的操作
            var action = 'add';
            if (sHandler.indexOf('has_comment_up') >= 0) {
                // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
                // $this.removeClass('has_comment_up')
                action = 'remove'
            }
            // else {
            //     $this.addClass('has_comment_up')
            // }
            var comment_id = $(this).attr('data-commentid');
            var params = {'action': action, 'comment_id': comment_id}


        $.ajax({
            url: '/news/like_comment',
            type: 'post',
            contentType: 'application/json',
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            data: JSON.stringify(params)
        })
            .done(function (response) {
                if (response.errno == '0') {
                    alert(response.errmsg);
                    var like_count = $this.attr('data-likecount');
                    if (like_count ==undefined){
                        like_count = 0;
                    }
                    if (action == 'add') {
                        like_count = parseInt(like_count) + 1;
                        $this.addClass('has_comment_up')
                    } else {
                        like_count = parseInt(like_count) - 1;
                        $this.removeClass('has_comment_up')
                    }
                    // 跟新点赞的数据
                    $this.attr('data-likecount', like_count);
                    if (like_count == 0) {
                            $this.html("赞")
                        }else {
                            $this.html(like_count)
                        }
                } else if (response.errno == '4101') {
                    $('.login_form_con').show()
                }
                else {
                    alert(response.errmsg)
                }
            })
            .fail(function () {
                alert('服务器超时，请重试!')
            });
        }

        // TODO 回复评论
        if(sHandler.indexOf('reply_sub')>=0)
        {
            // 获取html数据, 构造参数
            var $this = $(this);
            var params = {
                'news_id': $this.parent().attr('data-newsid'),
                'comment_id': $this.parent().attr('data-commentid'),
                'comment_content': $this.prev().val()
                };
            $.ajax({
                url:'/news/comment_comment',
                type:'post',
                contentType:'application/json',
                data:JSON.stringify(params),
                headers:{'X-CSRFToken': getCookie('csrf_token')}
            })
                .done(function (response) {
                    if (response.errno == '4101'){
                        $('.login_form_con').show()
                    }
                    else if (response.errno == '0'){
                        alert(response.errmsg);
                        // 接收data
                        var comment_user = response.data.children_comment.user;
                        var comment = response.data.children_comment;
                        // 拼接评论的回复html
                        var comment_html = '';
                        comment_html += '<div class="comment_list">';
                        comment_html += '<div class="person_pic fl">';
                        if (comment_user.avatar_url) {
                            comment_html += '<img src="' + comment_user.avatar_url + '" alt="用户图标">'
                        }else {
                            comment_html += '<img src="../../static/news/images/cat.png" alt="用户图标">'
                        }
                        comment_html += '</div>';
                        comment_html += '<div class="user_name fl">' + comment_user.nick_name + '</div>';
                        comment_html += '<div class="comment_text fl">';
                        comment_html += comment.content;
                        comment_html += '</div>';
                        comment_html += '<div class="reply_text_con fl">';
                        comment_html += '<div class="user_name2">' + comment.parent.user.nick_name + '</div>';
                        comment_html += '<div class="reply_text">';
                        comment_html += comment.parent.content;
                        comment_html += '</div>';
                        comment_html += '</div>';
                        comment_html += '<div class="comment_time fl">' + comment.create_time + '</div>';
                        comment_html += '<a href="javascript:;" class="comment_up fr" data-commentid="' + comment.id + '">赞</a>';
                        comment_html += '<a href="javascript:;" class="comment_reply fr">回复</a>';
                        comment_html += '<form class="reply_form fl" data-commentid="' + comment.id + '" data-newsid="' + comment.news_id + '">';
                        comment_html += '<textarea class="reply_input"></textarea>';
                        comment_html += '<input type="button" value="回复" class="reply_sub fr">';
                        comment_html += '<input type="reset" name="" value="取消" class="reply_cancel fr">';
                        comment_html += '</form>';
                        comment_html += '</div>';
                        // 添加到父评论之前
                        $(".comment_list_con").prepend(comment_html);
                        // 请空输入框
                        $this.prev().val('');
                        // 关闭
                        $this.parent().hide()
                    }
                    else{alert(response.errmsg)}
                })
                .fail(function () {
                    alert('服务器超时，请重试!')
                })
        }

        // TODO 删除评论
        if (sHandler.indexOf('comment_delete') >= 0) {
            // 获取参数
            var params = {
                'news_id': $(this).attr('data-newsid'),
                'comment_id': $(this).attr('data-commentid')
            }
            $.ajax({
                url:'/news/delete_comment',
                type:'post',
                contentType:'application/json',
                data:JSON.stringify(params),
                headers:{'X-CSRFToken': getCookie('csrf_token')}
            })
                .done(function (response) {
                    if (response.errno=='0'){
                        alert(response.errmsg)
                        window.location.reload()
                    }else if (response.errno=='4101'){
                        $('.login_form_con').show()
                    }else{
                        alert(response.errmsg)
                    }
                })
        }
    });

       // 关注当前新闻作者
    $(".focus").click(function () {

        var user_id = $(this).attr('data-userid')
        var params = {
            "action": "follow",
            "news_user_id": user_id
        }
        $.ajax({
            url: "/news/user_followed",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    alert(resp.errmsg);
                    // 关注成功
                    var count = parseInt($(".follows b").html());
                    count++;
                    $(".follows b").html(count + "")
                    $(".focus").hide ()
                    $(".focused").show()
                }else if (resp.errno == "4101"){
                    // 未登录，弹出登录框
                    $('.login_form_con').show();
                }else {
                    // 关注失败
                    alert(resp.errmsg)
                }
            }
        })

    })
    // 取消关注当前新闻作者
    $(".focused").click(function () {
        var user_id = $(this).attr('data-userid')
        var params = {
            "action": "unfollow",
            "news_user_id": user_id
        }
        $.ajax({
            url: "/news/user_followed",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (resp) {
                if (resp.errno == "0") {
                    alert(resp.errmsg)
                    // 取消关注成功
                    var count = parseInt($(".follows b").html());
                    count--;
                    $(".follows b").html(count + "")
                    $(".focus").show()
                    $(".focused").hide()
                }else if (resp.errno == "4101"){
                    // 未登录，弹出登录框
                    $('.login_form_con').show();
                }else {
                    // 取消关注失败
                    alert(resp.errmsg)
                }
            }
        })
        })
})
// 更新评论条数
function updateCommentCount() {
    var length = $(".comment_list").length
    $(".comment_count").html(length + "条评论")
}
var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = true;   // 是否正在向后台获取数据


$(function () {
    // 请求数据
    updateNewsData();
    // 首页分类切换
    $('.menu li').click(function () {
        // 点击标签的时候，回到页面顶部
        scrollTo(0, 0);
        var clickCid = $(this).attr('data-cid');
        $('.menu li').each(function () {
            $(this).removeClass('active')
        });
        $(this).addClass('active');

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid;
            // 重置分页参数
            cur_page = 1;
            total_page = 1;
            updateNewsData()
        }
    });

    //页面滚动加载相关
    $(window).scroll(function () {
        // 浏览器窗口高度
        var showHeight = $(window).height();
        // 整个网页的高度
        var pageHeight = $(document).height();
        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;
        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();
        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            if (!data_querying) {
                // 正在向后台获取数据， 当正在加载页面(请求数据)的时候，就不再获取新的数据
                data_querying = true;
                if (cur_page < total_page) {
                    cur_page += 1;
                    updateNewsData();
                }
            }
        }
    })
});

function updateNewsData() {
    // TODO 更新新闻数据
    var params = {
        'cid': currentCid,
        'page': cur_page
    };
    $.ajax({
        url: '/news_list',
        type:'get',
        data: params
    })
        .done(function (response) {
            // 向后台获取数据完毕(本页数据加载完成)
            data_querying = false;
            if (response.errno == '0'){
                // 得到响应记录total_page
                total_page = response.data.total_page;
                if(cur_page == 1){
                    // 清空新闻列表
                    $('.list_con').html('');
                }
                // 拼接html内容
                for (var i=0; i<response.data.news_list.length; i++){
                    var news = response.data.news_list[i];
                    var user = response.data.user_list[i];
                    var content = '<li>';
                    content += '<a href="/news/detail/'+news.id+'" class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>';
                    content += '<a href="/news/detail/'+news.id+'" class="news_title fl">' + news.title + '</a>';
                    content += '<a href="/news/detail/'+news.id+'" class="news_detail fl">' + news.digest + '</a>';
                    content += '<div class="author_info fl">';
                    if (user.id){
                        content += '<div class="author fl"><img src="'
                            if(user.avatar_url){content += user.avatar_url}
                            else{content += '../static/news/images/person01.png'}
                        content += '" alt="author"><a href="#">' + user.nick_name + '</a></div>';
                        }
                    else{content += '<div class="source fl">来源：' + news.source + '</div>';}
                    content += '<div class="time fl">' + news.create_time + '</div>';
                    content += ' </div></li>';
                    $('.list_con').append(content);}
            }else {alert(response.errmsg)}
        })
        .fail(function () {
            alert('服务器超时，请重试!')
        })
}

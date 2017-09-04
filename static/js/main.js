(function ($) {

    var mainInstance = {};
    // var ws = new WebSocket('ws://10.161.152.64:8000/soc');
    var ws = new WebSocket('ws://10.161.152.111:8000/soc');

    function init() {
        var client_number = $('#client_number').val();
        var initJson = {'type': 'init', 'client_number': client_number};
        ws.onopen = function () {
            ws.send(JSON.stringify(initJson));
        };
        ws.onmessage = function(event) {
            var data = JSON.parse(event.data);
            if (data.type == 'sys') {//系统通知
                $('#systemMessage').text(data.msg);
            }else if(data.type == 'online') {//朋友上线通知
                //如果已经在朋友列表中, 则更新client_number信息; 否则,添加一个
                var fromClientNumber = data.from_client_number;
                if ($('#client_' + fromClientNumber).length == 0) {
                    displayFriend(fromClientNumber);
                }
            }else if(data.type == 'offline'){
                var fromClientNumber = data.from_client_number;
                $('#client_' + fromClientNumber).remove();
                //关闭聊天窗口
                $('.right').addClass('none');
            }else if(data.type == 'user') {//朋友聊天消息
                var from = data.from_client_number;
                var pContent = '<div class="chatMessage"><p class="inMsg">' + data.msg + '</p></div>';
                refreshTalkWindow(from)
                $('#' + from).append(pContent);
                //收到消息的时候, 刷新一下在线的客户列表
                // initActiveClients();
                //自动将消息来源的人高亮,并且显示发送窗口
                $('.client_id').removeClass('active');
                $('#client_' + from).addClass('active');
            }
        };
        initActiveClients();
        bindEvents();
    }
    
    function bindEvents() {
        $('body').on('click', '.client_id', startTalk);
        $('body').on('click', '.sendContent', sendMsg);
        $(".talkContent").keydown(function (events) {
            if (events.keyCode == 13) {
                sendMsg();
                return false;
            }
        });
        $('body').on('click', '.logout', logout);
        $('.close_dialog').on('click', function () {
            $('.right').addClass('none');
        });
    }

    function logout() {
        var user = $('client_number').val();
        $.ajax({
            type: 'post',
            url: '/logout',
            data: {logout: user},
            success: function () {
                window.location.href = "/"
            }
        });
        return false;
    }

    /**
     * 点击好友时
     */
    function startTalk() {
        $(this).siblings().removeClass('active').end().addClass('active');
        $(".right").removeClass('none');
        //判断该好友的对话框是否存在
        var username = $(this).html();
        refreshTalkWindow(username)
    }

    function refreshTalkWindow(username) {
        $(".right").removeClass('none');
        var $dom = $("#" + username);
        if ($dom && $dom.length > 0) {
            $dom.siblings('.chatWindow').addClass('none').end().removeClass('none');
        }else {
            var newWindow = $('#exampleWindow').clone(true);
            newWindow.attr('id', username);
            $('#chatMsg').append(newWindow);
            newWindow.siblings('.chatWindow').addClass('none').end().removeClass('none');
        }
        $('#chatFriend .friend').html(username);
    }
    function sendMsg() {
        var msg = $('.talkContent').val();
        var toClient = $('.active').html();
        var pContent = '<div class="chatMessage"><p class="outMsg">' + msg + '</p></div>';
        $('#' + toClient).append(pContent);
        ws.send(JSON.stringify({to: toClient, message:msg}));

        $('.talkContent').val('');
    }

    /**
     * 展示一个朋友
     * @param fromClientNumber
     */
    function displayFriend(fromClientNumber) {
        var sinClient = '<a id="client_' + fromClientNumber + '"  href="javascript:void(0)" class="client_id">' + fromClientNumber + '</a>';
        $('#activeClientsList').append(sinClient);
    }

    /**
     * 获取活动的clients列表并显示
     */
    function initActiveClients() {
        var selfClientNumber = $('#client_number').val();
        $.ajax({
            type: 'GET',
            url: '/clients',
            dataType: 'json',
            success: function (data) {
                    $('.client_id').remove();
                    for (var i in data) {
                        if (data[i] == selfClientNumber) {
                            continue;
                        }
                        displayFriend(data[i]);
                    }
            }
        });
    }
    init();
    return mainInstance;
})(jQuery);
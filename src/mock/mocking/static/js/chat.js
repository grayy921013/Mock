$(function () {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var interview_id = $("#interview_id").html();
    var use_id = $("#user_id").html();
    var owner_id = $("#owner_id").html();
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/interview/" + interview_id);

    if (owner_id != use_id) {
        $("#code").prop('disabled', true);
    }
    chatsock.onmessage = function (message) {
        var data = JSON.parse(message.data);
        var textarea = $("#code");

        textarea.val(data.message);
    };

    $('#code').bind('input propertychange', function () {
        var message = {
            handle: use_id,
            message: $('#code').val()
        };
        chatsock.send(JSON.stringify(message));
    });
});

$(function () {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var interview_id = $("#interview_id").html();
    var use_id = $("#user_id").html();
    var owner_id = $("#owner_id").html();
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/interview/" + interview_id);
    var textarea = $("#code");
    var prevCode = textarea.val();

    if (owner_id != use_id) {
        textarea.prop('disabled', true);
    }
    chatsock.onmessage = function (message) {
        var data = JSON.parse(message.data);
        if (data.handle == use_id) return;
        textarea.val(prevCode.substring(0, data.start + 1) + data.change + prevCode.substring(data.end));
        prevCode = textarea.val();
    };

    textarea.bind('input propertychange', function () {
        var codeNow = textarea.val();
        var i = 0, j1 = prevCode.length - 1, j2 = codeNow.length - 1;
        while (i <= j1 && i <= j2) {
            if (prevCode.charAt(i) != codeNow.charAt(i)) break;
            i++;
        }
        while (i <= j1 && i <= j2) {
            if (prevCode.charAt(j1) != codeNow.charAt(j2)) break;
            j1--;
            j2--;
        }
        var message = {
            handle: use_id,
            start: i - 1,
            end: j1 + 1,
            change: codeNow.substring(i, j2 + 1)
        };
        chatsock.send(JSON.stringify(message));
        console.log(prevCode.substring(0, i) + codeNow.substring(i, j2 + 1) + prevCode.substring(j1 + 1));
        prevCode = codeNow;
    });

});

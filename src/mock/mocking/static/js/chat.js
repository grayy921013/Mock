$(function () {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var interview_id = $("#interview_id").html();
    var use_id = $("#user_id").html();
    var owner_id = $("#owner_id").html();
    var codesock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/interview/" + interview_id);
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat/" + interview_id);
    var textarea = $("#code");
    var prevCode = textarea.val();

    if (owner_id != use_id) {
        textarea.prop('disabled', true);
        textarea.prop('autofocus', false);
    } else {
        textarea.prop('disabled', false);
        textarea.prop('autofocus', true);
    }
    codesock.onmessage = function (message) {
        var data = JSON.parse(message.data);
        if (data.handle == use_id) return;
        textarea.val(prevCode.substring(0, data.start + 1) + data.change + prevCode.substring(data.end));
        prevCode = textarea.val();
    };

    chatsock.onmessage = function (message) {
        var data = JSON.parse(message.data);
        var chat = $("#chat");
        var ele = $('<tr></tr>');

        ele.append(
            $("<td></td>").text(data.created_at)
        );
        ele.append(
            $("<td></td>").text(data.handle)
        );
        ele.append(
            $("<td></td>").text(data.message)
        );

        chat.append(ele)
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
        codesock.send(JSON.stringify(message));
        console.log(prevCode.substring(0, i) + codeNow.substring(i, j2 + 1) + prevCode.substring(j1 + 1));
        prevCode = codeNow;
    });


    $("#chatform").on("submit", function(event) {
        event.preventDefault();
        var message = {
            message: $('#message').val()
        };
        chatsock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });
});

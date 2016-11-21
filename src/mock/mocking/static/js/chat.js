$(function () {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var interview_id = $("#interview_id").html();
    var use_id = $("#user_id").html();
    var owner_id = $("#owner_id").html();
    var sock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/interview/" + interview_id);
    var textarea = $("#code");
    var prevCode = textarea.val();
    var my_name = $("#user_name").html();

    sock.onmessage = function (message) {
        var data = JSON.parse(message.data);
        if (data.type == "code") {
            if (data.handle == use_id) return;
            textarea.val(prevCode.substring(0, data.start + 1) + data.change + prevCode.substring(data.end));
            prevCode = textarea.val();
        } else if (data.type == "chat") {
            var chat = $("#chat");
            var ele = $('<li/>').addClass("mar-btm");

            var div = $("<div/>");
            if (data.handle == my_name) {
                div.addClass("speech-right");
            } else {
                div.addClass("media-body pad-hor");
            }

            var speech = $("<div/>").addClass("speech");

            speech.append(
                $("<div/>").addClass("media-heading").text(data.handle)
            );
            speech.append(
                $("<strong/>").text(data.message)
            );

            div.append(speech);
            ele.append(div);
            chat.append(ele);
        } else if (data.type == "time") {
            if (data.time > 0 && owner_id == use_id) {
                textarea.prop('disabled', false);
                textarea.prop('autofocus', true);
            } else {
                textarea.prop('disabled', true);
                textarea.prop('autofocus', false);
            }
            if (data.time > 0) {
                var now = new Date();
                now.setSeconds(now.getSeconds() + data.time);
                $("#clock").countdown(now)
                    .on('update.countdown', function (event) {
                        $(this).text(
                            event.strftime('%M m:%S s')
                        );
                    }).on('finish.countdown', function (event) {
                    alert("time up!");
                    textarea.prop('disabled', true);
                    textarea.prop('autofocus', false);
                });
            }
        }
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
            type: "code",
            handle: use_id,
            start: i - 1,
            end: j1 + 1,
            change: codeNow.substring(i, j2 + 1)
        };
        sock.send(JSON.stringify(message));
        console.log(prevCode.substring(0, i) + codeNow.substring(i, j2 + 1) + prevCode.substring(j1 + 1));
        prevCode = codeNow;
    });


    $("#chatform").on("submit", function (event) {
        event.preventDefault();
        var message = {
            type: "chat",
            message: $('#message').val()
        };
        sock.send(JSON.stringify(message));
        $("#message").val('').focus();
        return false;
    });
});

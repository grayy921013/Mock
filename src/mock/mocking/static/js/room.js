$(function () {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var interview_id = $("#interview_id").html();
    var use_id = $("#user_id").html();
    var owner_id = $("#owner_id").html();
    var sock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/interview/" + interview_id);
    var textarea = $("#code1");
    var prevCode = textarea.val();
    var my_name = $("#user_name").html();
    var modal = $("#rate_modal");
    var chat_btn = $("#go");

    var lang = $("#language");
    var editor = CodeMirror.fromTextArea(document.getElementById("code1"), {
        lineNumbers: true,
        mode: "text/x-cython"
    });
    editor.on("change", function () {
        console.log(editor.getValue());
        var codeNow = editor.getValue();
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
    // hide or show problem according to users' role
    lang.change(function () {
        if (lang.val() == "Java") {
            editor.setOption("mode", "text/x-java");
        }
        else if (lang.val() == "Python") {
            editor.setOption("mode", "text/x-cython");
        }
        else if (lang.val() == "C++") {
            editor.setOption("mode", "text/x-c++src");
        }
    });

    // WebSocket callbacks
    sock.onmessage = function (message) {
        var data = JSON.parse(message.data);
        if (data.type == "code") {
            if (data.handle == use_id) return;
            editor.setValue(prevCode.substring(0, data.start + 1) + data.change + prevCode.substring(data.end));
            prevCode = editor.getValue();
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
                editor.setOption("readOnly", false);
            } else {
                editor.setOption("readOnly", "nocursor");
            }
            if (data.time > 0) {
                var now = new Date();
                now.setSeconds(now.getSeconds() + data.time);
                chat_btn.prop('disabled', false);
                $("#clock").countdown(now)
                    .on('update.countdown', function (event) {
                        $(this).text(
                            event.strftime('%M m:%S s')
                        );
                    }).on('finish.countdown', function (event) {
                    alert("time up!");
                    editor.setOption("readOnly", "nocursor");
                    $("#clock").html("");
                    chat_btn.prop('disabled', true);
                    // pop up rating form
                    modal.modal('show');
                });
            } else {
                $.get("/mocking/get_rate_record?interview=" + interview_id).done(function (data) {
                    if (data.result == 404) {
                        // pop up rating form
                        modal.modal('show');
                    }
                });
            }
        }
    };


    // chat form submission
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

    // rate form submission

    var rate_form = $("#rate_form");
    rate_form.on("submit", function (event) {
        event.preventDefault();
        $.post("/mocking/rate", rate_form.serialize())
            .done(function (data) {
                console.log(data);
            });
        modal.modal("hide");
    });


});



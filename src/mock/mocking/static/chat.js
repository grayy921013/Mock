$(function() {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + "52.204.8.61:8000" + "/interview/1/");

    chatsock.onmessage = function(message) {
        var data = JSON.parse(message.data);
        var textarea = $("#message");

        textarea.val(data.message);
    };

    $("#chatform").on("submit", function(event) {
        var message = {
            handle: 1,
            message: $('#message').val(),
        }
        chatsock.send(JSON.stringify(message));
        return false;
    });
});

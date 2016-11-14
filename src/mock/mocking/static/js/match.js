$(function () {
    // When we're using HTTPS, use WSS too.
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var match_btn1 = $("#match_btn1");
    match_btn1.on('click', function () {
        var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/match/0/1");

        chatsock.onmessage = function (message) {
            console.log(message);
            console.log("match succeed!");
            window.location.replace("http://" + window.location.host + "/mocking/interview/" + message.data);
        };
    });

    var match_btn2 = $("#match_btn2");
    match_btn2.on('click', function () {
        var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/match/1/1");

        chatsock.onmessage = function (message) {
            console.log(message);
            console.log("match succeed!");
            window.location.replace("http://" + window.location.host + "/mocking/interview/" + message.data);
        };
    });

});

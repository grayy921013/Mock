/**
 * Created by ClownXiao on 16/11/15.
 */

var chatsock = null;

$(document).ready(function () {
    var role = $("#id_role");
    var problem = $("#id_problem");
    roleChanged(role);

    // hide or show problem according to users' role
    role.change(function () {
        roleChanged(role);
    });

    problem.change(function () {
        $('#problem').empty();
        $.get("/mocking/get_problem/" + problem.val())
            .done(function (data) {

                updateProblem(data);
            });
    });

    // websocket code for matching
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var match_btn = $("#match_btn");
    match_btn.on('click', function (event) {
        event.preventDefault();
        if (chatsock == null) {
            chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/match/" + role.val() + "/" + problem.val());

            chatsock.onmessage = function (message) {
                console.log(message);
                console.log("match succeed!");
                window.location.href = "http://" + window.location.host + "/mocking/interview/" + message.data;
            };
            chatsock.onopen = function () {
                match_btn.html("Stop");
            };
            chatsock.onclose = function () {
                chatsock = null;
                match_btn.html("Match");
            };
        } else {
            chatsock.close();
            chatsock = null;
        }
    });
});

//function to call if role changed
function roleChanged(role) {
    var problem = $("#id_problem");
    if (role.val() == '1') {
        // role is interviewee
        problem.hide();
        $('#problem').empty();
        problem.prop('required', false);
    }
    else {
        // role is interviewer
        problem.show();
        problem.prop('required', true);
    }
}


//change problem detail according to user's choice on "id_problem"
function updateProblem(data) {
    var div = $('#problem');
    div.empty();

    var p_id = $('<p>');
    p_id.html("problem id: " + data.data.id);
    var p_name = $('<p>');
    p_name.html("problem name: " + data.data.name);
    var p_description = $('<p>');
    p_description.html("problem description: " + data.data.description);
    var p_difficulty = $('<p>');
    p_difficulty.html("problem difficulty: " + data.data.difficulty);
    var p_solution = $('<p>');
    p_solution.html("problem solution: " + data.data.solution);

    p_id.appendTo(div);
    p_name.appendTo(div);
    p_difficulty.appendTo(div);
    p_description.appendTo(div);
    p_solution.appendTo(div)

}
/**
 * Created by ClownXiao on 16/11/15.
 */



$(document).ready(function () {
    var role = $("#id_role");
    var problem = $("#id_problem");
    problem.hide();

    // hide or show problem according to users' role
    role.change(function(){
        if(role.val() == '1')
            problem.hide();
        else
            problem.show();

    });

    problem.change(function(){
        $.get("/mocking/get_problem/" + problem.val())
            .done(function (data) {

            updateProblem(data);
        });
    });


});


//change problem detail according to user's choice on "id_problem"
function updateProblem(data) {
    var div = $('#problem');
    div.empty();

    var p_id = $('<p>');
    p_id.html("problem id: " + data.data.id);
    var p_name = $('<p>');
    p_name.html("problem name: " + data.data.name);
    var p_description= $('<p>');
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
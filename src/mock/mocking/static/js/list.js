/**
 * Created by admin on 11/3/16.
 */
// create_interview_btn = $("#create_interview_btn");
// create_interview_btn.on('click', create_interview);
//
// function create_interview() {
//     $.ajax({url: "/mocking/create_interview", method: "post", data: {'csrfmiddlewaretoken':csrftoken}})
//         .done(function () {
//             $.ajax({url: "/mocking/get_interview_list", method: "get"})
//                 .done(function(data){
//                     update_list(data);
//                 });
//          })
//         .fail(function () {
//             alert("fail");
//         });
// }

// update list
function update_list(data) {

    // Display new messages
    //$('#message').text(data.result);
    var ls = $("#interview-list");
    ls.empty();
    // Process lists
    for (var i = 0; i < data.data.length; i++) {
        //alert(data.interview_list[i].id)
        var div = $("<div>");
        div.attr({
            "id": data.data[i].id,
            "class": "panel-body"
        });
        var p = $("<a>");
        p.html("interview-" + data.data[i].id);
        p.appendTo(div);
        p.attr({
            "href" : "interview/" + data.data[i].id
        });
        var p_name = $("<p>");
        p_name.addClass("interviewer_name");
        p_name.html("interviewer: " + data.data[i].interviewer_name);
        p_name.appendTo(div);
        p_name = $("<p>");
        p_name.addClass("interviewer_name");
        p_name.html("interviewee: " +data.data[i].interviewee_name);
        p_name.appendTo(div);
        var hr = $("<hr>");
        hr.appendTo(div);
        div.appendTo(ls);
        ls.append(div);
    }

}

$(document).ready(function () {
    $.ajax({url: "/mocking/get_interview_list", method: "get"})
                .done(function(data){
                    update_list(data);
                });
});

function getCookie(name) {


    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var csrftoken = getCookie('csrftoken');
/**
 * Created by ClownXiao on 16/11/29.
 */


// update list
function update_list(data) {

    // Display new message
    var ls = $("#board-list");
    //ls.empty();
    // Process lists
    for (var i = 0; i < data.data.length; i++) {
        var div = $("<div>");
        div.attr({
            "id": data.data[i].id,
            "class": "panel-body",
            "float": "left"
        });
        var tr = $("<tr>");
        var td1 = $("<td>");
        td1.attr({
            "class": 'table-td-rank'
        })

        var rank = $("<p>");
        rank.attr({
            "class": "table-num"
        });
        rank.html((i + 1));
        rank.appendTo(td1);

        var td2 = $("<td>");
        td2.attr({
            "class": 'table-td'
        })
        var p = $("<a>");
        p.html(data.data[i].first_name + " " + data.data[i].last_name);
        p.appendTo(td2);
        p.attr({
            "href" : "get_profile/" + data.data[i].id
        });

        var image = $("<img>")
        image.attr({
            "class" : "small-header",
            "alt" : "avatar",
            "src" : "get_avatar/" + data.data[i].userid
        });
        image.appendTo(td2);
        p.appendTo(td2);

        var td3 = $("<td>");
        td3.attr({
            "class": 'table-td'
        })
        var p_name = $("<p>");
        p_name.addClass("interviewer_name");
        p_name.html("rating " + data.data[i].rating);
        p_name.appendTo(td3);

        td1.appendTo(tr);
        td2.appendTo(tr);
        td3.appendTo(tr);
        tr.appendTo(div);
        var hr = $("<hr>");
        hr.appendTo(div);
        ls.append(div);









        /*var div = $("<div>");
        div.attr({
            "id": data.data[i].id,
            "class": "panel-body",
            "float": "left"
        });
        var rank = $("<p>");
        rank.html((i + 1));
        rank.appendTo(div);

        var image = $("<img>")
        image.attr({
            "class" : "small-header",
            "alt" : "avatar",
            "src" : "get_avatar/" + data.data[i].userid
        });
        image.appendTo(div);

        var p = $("<a>");
        p.html(data.data[i].first_name + " " + data.data[i].last_name);
        p.appendTo(div);
        p.attr({
            "href" : "get_profile/" + data.data[i].id
        });

        var p_name = $("<p>");
        p_name.addClass("interviewer_name");
        p_name.html("rating " + data.data[i].rating);
        p_name.appendTo(div);
        var hr = $("<hr>");
        hr.appendTo(div);
        div.appendTo(ls);
        ls.append(div);*/
    }

}

$(document).ready(function () {
    $.ajax({url: "/mocking/get_rate_board", method: "get"})
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
/*
$(document).ready(function () {
	var x = document.getElementsByClassName("media-heading");
	for (var i = 0; i < x.length; i++ ) {
		if (x[i].innerHTML == $("#user_name").html()) {
			x[i].parentElement.parentElement.className = "speech-right";
		}

	}
});*/


function refresh() {

	var x = document.getElementsByClassName("media-heading");
	for (var i = 0; i < x.length; i++ ) {
		if (x[i].innerHTML == $("#user_name").html()) {
			x[i].parentElement.parentElement.className = "speech-right";
		}

	}
}
window.setInterval(refresh, 100);
var divCopy = document.getElementById('copyText'),
  nmbrBox = document.getElementById('numbers'),
  txtBox = document.getElementById('textBox'),
  lineHeight = 20;

/*This function copies the text from the textarea to a div 
  so we can check the height and then get the number of lines 
  from that information*/
function copyText() {
  "use strict";

  //variable to hold and manipulate the value of our textarea
  var txtBoxVal = txtBox.value;

  //regular expression to replace new lines with line breaks
  txtBoxVal = txtBoxVal.replace(/(?:\r\n|\r|\n)/g, '<br />');

  //copies the text from the textarea to the #copyText div
  divCopy.innerHTML = txtBoxVal;
}

function addLines() {
  "use strict";
  var lines = divCopy.offsetHeight / lineHeight, x = 1, holder = '';
  for (x = 1; x <= lines; x = x + 1) {
    holder += '<div class="row">' + x + '.</div>';
  }
  if (lines === 0) {
    holder = '<div class="row">1.</div>';
  }
  nmbrBox.innerHTML = holder;
}


//Bind events to elements
function addEvents() {
  "use strict";
  txtBox.addEventListener("keyup", copyText, false);
  txtBox.addEventListener("keyup", addLines, false);
}

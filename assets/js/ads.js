$(document).ready(function() {

  $('.submit_on_enter').keydown(function(event) {
    // enter has keyCode = 13, change it if you want to use another button
    if (event.keyCode == 13 || event.keyCode == 10) {
      this.form.submit();
      return false;
    }
  });

});

$("#vk_form :input").tooltip({
 position: "center right",
 offset: [-2, 10],
 effect: "fade",
 opacity: 0.7
});

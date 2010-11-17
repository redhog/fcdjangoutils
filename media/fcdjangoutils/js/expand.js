$(document).ready(function () {
  $('.autohide-body').hide();
  $('.autohide-button').click(function () {
    var id = this.id.replace(new RegExp("-button$"), "");
    $('#' + id + '-body').toggle(500);
  });
});

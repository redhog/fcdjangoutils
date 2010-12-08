$(document).ready(function () {
  $('.autohide-body').hide();
  $('.autohide-button').click(function () {
    var id = this.id.replace(new RegExp("-button$"), "");
    $(this).toggleClass('autohide-expanded');
    $('#' + id + '-body').toggle(500);
  });
});

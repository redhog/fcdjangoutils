expand = {};

expand.prepare = function () {
  //$('.autohide-body').hide();
  $('.autohide-button').click(function () {
    var id = this.id.replace(new RegExp("-button$"), "");
    $(this).toggleClass('autohide-expanded');
    $('#' + id + '-body').toggle(500);
  });

  $('.new_comment').focus(function() {
      var comment = $(this);
      comment.addClass('expanded', 200);
      comment.parent().next('button.submit_comment').show();
    });
}

$(document).ready(expand.prepare);

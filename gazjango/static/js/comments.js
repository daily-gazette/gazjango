var speed = 'normal';

function hideFunctionFor(id) {
  return function() {
    $('#c-' + id)
      .find('.commentText').slideUp(speed).end()
      .find('.showLink')
        .html('show anyway')
        .unbind('click')
        .click(showFunctionFor(id));
    return false;
  };
}
function showFunctionFor(id) {
  return function() {
    $('#c-' + id)
      .find('.commentText').slideDown(speed).end()
      .find('.showLink')
        .html('hide')
        .unbind('click')
        .click(hideFunctionFor(id));
    return false;
  };
}

$(document).ready(function() {
  $('.comment').each(function(i) {
    var comment = this;
    var id = comment.id.substring('2');
    
    $(comment).find('.showLink').click(function(obj) {
      $(comment)
        .find('.commentText')
          .hide()
          .load('show-comment/' + id + '/', function() {
            $(this).slideDown(speed);
          })
          .end()
        .find('.showLink')
          .html('hide')
          .unbind('click')
          .click(hideFunctionFor(id));
      return false;
    });
  });
});

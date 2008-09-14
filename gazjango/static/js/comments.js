/*
    TODO: show links for new comments don't work
    TODO: when a comment is posted, highlight it and clear the form
*/

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

function setupShowLinks() {
  $('.comment').each(function() {
    var comment = this;
    var id = comment.id.substring('2');
    
    $(comment).find('.showLink')
        .unbind('click')
        .click(function(obj) {
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
}

$(document).ready(setupShowLinks);


var default_comment_name;
$(document).ready(function() {
   default_comment_name = $('input[name="name"]').val();
});

function toggleNameDisabled() {
    namebox = $('input[name="name"]');
    if (namebox.attr('disabled')) {
        namebox.attr('disabled', false);
    } else {
        namebox.val(default_comment_name);
        namebox.attr('disabled', true);
    }
}

function refreshComments() {
    $('#comments').load('comments/');
    setupShowLinks();
}

function newComments() {
    // doesn't seem to work
    comments = $('#comments .comment');
    if (comments.length > 0) {
        last_num = 0;
    } else {
        last_num = comments.eq(comments.length - 1).id.substr(2);
    }
    $.get('comments/' + last_num + '/', {}, function(data, textStatus) {
       $('#comments').append(data);
    });
}


function submitComment() {
    data = {};
    $('#commentForm :input').each(function() {
        data[$(this).attr('name')] = $(this).val();
    });
    
    alert('foo');
    $.post($('#commentForm form').attr('action'), data,
       function(resp, textStatus) {
           alert('lol');
           if (resp == 'success') {
               refreshComments();
           } else {
               // it's okay to kill the <h4>, since it's unlikely that
               // many people will have javascript on but css off :)
               $('#commentForm').html(resp);
           }
       }
    );
    return false;
}
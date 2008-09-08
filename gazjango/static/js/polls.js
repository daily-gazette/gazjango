function submitPoll(num) {
    var poll = $('#poll-' + num);

    $.post(
        poll.find('form').attr('action'),
        { option: poll.find('input:radio:checked').val() },
        function(data, textStatus) {
            if (textStatus != 'success') {
                alert('Weird error, sorry.');
            } else {
                if (data == 'success') {
                    showPollResults(num);
                } else {
                    poll.find('.poll-question')
                        .after('<div class="poll-error">'+data+'</div>');
                    showPollResults(num);
                }
            }
        }
    );
}

function showPollResults(num) {
    var poll = $('#poll-' + num);
    var show_results = poll.find('.show-results');
    poll.find('.other-content').hide().load(
        show_results.find('a').attr('href'),
        function() {
            poll.find('.poll-voting').hide('slow').end()
                .find('.other-content').show('slow');
            show_results.hide(0);
        }
    );
}
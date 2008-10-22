from django.http      import HttpResponse
from django.template  import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from gazjango.polls.models      import Poll
from gazjango.misc.view_helpers import get_ip
import gazjango.polls.exceptions

def poll_results(request, year, slug, template="polls/results.html"):
    poll = get_object_or_404(Poll, time_start__year=year, slug=slug)
    rc = RequestContext(request)
    return render_to_response(template, {'poll': poll}, context_instance=rc)


def submit_poll(request, year=None, slug=None):
    if request.method != 'POST':
        return HttpResponse('POST or gtfo')
    else:
        print repr(request.POST['option'])
        poll = get_object_or_404(Poll, time_start__year=year, slug=slug)
        
        ip = get_ip(request)
        if request.user.is_authenticated():
            user = request.user.get_profile()
        else:
            user = None
        
        option_pk = request.POST['option']
        try:
            option = poll.options.get(pk=option_pk)
        except:
            return HttpResponse('error: invalid option "%s"' % option_pk)
        
        try:
            poll.vote(option=option, user=user, ip=ip)
        except gazjango.polls.exceptions.NotVoting:
            return HttpResponse("This poll is not accepting votes at this time.")
        except gazjango.polls.exceptions.AlreadyVoted:
            return HttpResponse("You've already voted in this poll.")
        except gazjango.polls.exceptions.PermissionDenied:
            return HttpResponse("You're not allowed to vote in this poll.")
        except Exception, e:
            return HttpResponse("Unknown problem: " + repr(e))
        else:
            if request.is_ajax():
                return HttpResponse('success')
            else:
                return HttpResponseRedirect(poll.get_absolute_url())

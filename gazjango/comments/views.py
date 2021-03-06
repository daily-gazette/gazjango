from collections                    import defaultdict

from django.conf                    import settings
from django.db.models               import Q
from django.http                    import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts               import render_to_response
from django.template                import RequestContext
from django.utils.html              import escape

from gazjango.articles.models      import Article
from gazjango.articles.views       import specific_article
from gazjango.comments.forms       import make_comment_form
from gazjango.comments.models      import PublicComment, CommentIsSpam
from gazjango.misc                 import recaptcha
from gazjango.misc.view_helpers    import get_ip, get_user_profile, is_robot
from gazjango.misc.view_helpers    import get_by_date_or_404, boolean_arg
from gazjango.announcements.models import Poster



def comment_page(request):
    'View for all recent comments'
    comments = PublicComment.visible.order_by('-time').select_related(depth=1).all()[:20]
    
    comment_list = defaultdict(lambda: [])
    for comment in comments:
        comment_list[comment.subject].insert(0,comment)
    final_list = sorted(comment_list.values(), key=lambda lst: lst[-1].time, reverse=True)

    rc = RequestContext(request, {
        'comments': final_list,
        'poster': Poster.published.get_running(),
        
    })
    return render_to_response('comment/index.html', context_instance=rc)    
    
def post_comment(request, slug, year, month, day):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    if not story.comments_allowed:
        raise Http404 # semantically incorrect, but whatever
    
    logged_in = request.user.is_authenticated()
    staff = logged_in and get_user_profile(request).staff_status()
    form = make_comment_form(data=request.POST, logged_in=logged_in, staff=staff)
    
    if form.is_valid():
        data = form.cleaned_data
        args = {
            'subject': story,
            'text': escape(data['text']).replace("\n", "<br/>"),
            'ip_address': get_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')
        }
        
        if logged_in:
            args['user'] = get_user_profile(request)
            if data['anonymous']:# and data['name'] != request.user.get_full_name():
                args['name'] = data['name']
            args['speaking_officially'] = data['speaking_officially']
        else:
            args['name']  = data['name']
            args['email'] = data['email']
        
        try:
            comment = PublicComment.objects.new(**args)    
        except CommentIsSpam, e:
            # put data in the session, because we're silly like that
            url = e.comment.subject.get_absolute_url()
            request.session.set_expiry(0)
            request.session['comment:%s' % url] = e.comment
            
            # NOTE: coupling with url for comment captchas
            redirect = request.build_absolute_uri(url + 'comment/captcha')
            if request.is_ajax():
                return HttpResponse('redirect: %s' % redirect)
            else:
                return HttpResponseRedirect(redirect)
        
        if request.is_ajax():
            return HttpResponse('success')
        else:
            return HttpResponseRedirect(comment.get_absolute_url())
    else:
        if request.is_ajax():
            template = "stories/comment_form.html"
            rc = RequestContext(request, { 'comment_form': form })
            return render_to_response(template, context_instance=rc)
        else:
            return specific_article(request, story, form=form)


def show_captcha(request, year, month, day, slug):
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    key = 'comment:%s' % story.get_absolute_url()
    try:
        comment = request.session[key]
    except KeyError:
        raise Http404
    
    url = "http://api.recaptcha.net/%s?k=" + settings.RECAPTCHA_PUBLIC_KEY
    if "recaptcha_response_field" in request.POST:
        result = recaptcha.submit(request.POST.get('recaptcha_challenge_field', None),
                                  request.POST.get('recaptcha_response_field',  None),
                                  settings.RECAPTCHA_PRIVATE_KEY,
                                  get_ip(request))
        if result.is_valid:
            del request.session[key]
            comment.mark_as_ham()
            comment.save()
            if request.is_ajax():
                # we're not (yet) doing this via ajax, so it's ok 
                raise NotImplemented
            else:
                return HttpResponseRedirect(comment.get_absolute_url())
        else:
            url += "&error=%s" % response.error_code
    
    rc = RequestContext(request, { 'challenge_captcha_url': url % 'challenge',
                                   'noscript_captcha_url':  url % 'noscript' })
    return render_to_response('stories/captcha_form.html', context_instance=rc)


def comments_for_article(request, slug, year, month, day, num=None):
    """
    Returns the comments for the specified article, rendered as they are
    on article view pages, starting after number `num`. Used for after
    you've posted an AJAX comment.
    """
    story = get_by_date_or_404(Article, year, month, day, slug=slug)
    
    user = get_user_profile(request)
    ip = get_ip(request)
    
    spec = Q(number__gt=num) if num else Q()
    comments = PublicComment.objects.for_article(story, user, ip, spec=spec)
    
    rc = RequestContext(request, { 'comments': comments, 'new': True })
    return render_to_response("stories/comments.html", context_instance=rc)


def _get_comment_or_404(year, month, day, slug, num):
    try:
        return PublicComment.objects.get(article__pub_date__year=year,
                                         article__pub_date__month=month,
                                         article__pub_date__day=day,
                                         article__slug=slug,
                                         number=num)
    except PublicComment.DoesNotExist:
        raise Http404


def get_comment_text(request, slug, year, month, day, num):
    return HttpResponse(_get_comment_or_404(year, month, day, slug, num).text)


def vote_on_comment(request, slug, year, month, day, num, val):
    if is_robot(request):
        return HttpResponse('sorry, you seem to be a robot, no voting for you!')
    
    comment = _get_comment_or_404(year, month, day, slug, num)
    positive = (val == 'up') if val in ('up', 'down') else None
    result = comment.vote(positive, ip=get_ip(request), user=get_user_profile(request))
    
    if request.is_ajax():
        return HttpResponse("success" if result else "failure")
    else:
        return HttpResponseRedirect(comment.get_absolute_url())


def approve_comment(request, slug, year, month, day, num, val='1'):
    if not request.user.has_perm('comments.change_publiccomment'):
        if request.is_ajax():
            raise Http404
        else:
            return HttpResponseRedirect("%s?next_page=%s" % (settings.LOGIN_URL, request.path))
    
    comment = _get_comment_or_404(year, month, day, slug, num)
    approve = boolean_arg(val, default=True)
    
    if bool(comment.is_approved) != approve:
        comment.is_approved = approve
        comment.save()
    
    if request.is_ajax():
        return render_to_response('comment/authorship.html', {
            'comment': comment,
        }, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(comment.get_absolute_url())
    

from django.shortcuts       import get_object_or_404, render_to_response
from django.template        import RequestContext

from gazjango.articles.models  import Section
from gazjango.athletics.models import Team, Game

from gazjango.articles.models      import Article   
    

def athletics(request):
    'View for "athletic" team pages.'     
        
    start_trimester = Game.objects.latest().team.trimester
    current_trimester = Team.objects.filter(trimester=start_trimester).order_by("sport","gender") 
    
    section = Section.objects.get(slug='athletics')
    article_list = section.published_articles().order_by("-pub_date")
    
    
    rc = RequestContext(request, { 'trimester': current_trimester, 'article_list': article_list })
    return render_to_response('athletics/index.html', context_instance=rc)



def team(request, slug):
    'View for "athletic" team pages.'
    
    team = get_object_or_404(Team, slug=slug)
    
    rc = RequestContext(request, { 'team': team })
    return render_to_response('athletics/team.html', context_instance=rc)

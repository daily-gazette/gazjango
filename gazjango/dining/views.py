from django.shortcuts       import get_object_or_404, render_to_response
from django.template        import RequestContext

from gazjango.articles.models  import Section
from gazjango.dining.models    import Establishment

from gazjango.articles.models  import Article   
    

def reviews(request):
    'View for "establishment review" page.'
    section = Section.objects.get(slug='reviews')
    
    establishments = Establishment.objects.order_by("establishment_type","name")
     
        
    start_trimester = Game.objects.latest().team.trimester
    current_trimester = Team.objects.filter(trimester=start_trimester).order_by("sport","gender") 
    
    article_list = section.published_articles().order_by("-pub_date")
    
    
    rc = RequestContext(request, {})
    return render_to_response('reviews/index.html', context_instance=rc)
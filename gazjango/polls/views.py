from django.template  import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

poll            = lambda request, **kwargs: render_to_response("base.html", locals())
polls_for_year  = lambda request, **kwargs: render_to_response("base.html", locals())
polls_for_month = lambda request, **kwargs: render_to_response("base.html", locals())
polls_for_day   = lambda request, **kwargs: render_to_response("base.html", locals())

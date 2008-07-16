from django.shortcuts import render_to_response

manage       = lambda request, **kwargs: render_to_response("base.html", locals())
register     = lambda request, **kwargs: render_to_response("base.html", locals())
user_details = lambda request, **kwargs: render_to_response("base.html", locals())

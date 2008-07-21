from django.shortcuts import render_to_response

announcement            = lambda request, **kwargs: render_to_response("base.html", locals())
announcements           = lambda request, **kwargs: render_to_response("base.html", locals())

kind           = lambda request, **kwargs: render_to_response("base.html", locals())
kind_for_year  = lambda request, **kwargs: render_to_response("base.html", locals())
kind_for_month = lambda request, **kwargs: render_to_response("base.html", locals())
kind_for_day   = lambda request, **kwargs: render_to_response("base.html", locals())


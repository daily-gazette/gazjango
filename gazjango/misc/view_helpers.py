from django.shortcuts import get_object_or_404

def get_by_date_or_404(model, year, month, day, field='pub_date', **oth):
    d = oth
    d.update({field+'__year': year, field+'__month': month, field+'__day': day})
    return get_object_or_404(model, **d)

def filter_by_date(qset, year=None, month=None, day=None, field='pub_date'):
    args = {}
    if year:
        args[field + '__year'] = year
        if month:
            args[field + '__month'] = month
            if day:
                args[field + '__day'] = day
    return qset.filter(**args)


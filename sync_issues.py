from interactive_load import *

import csv
reader = csv.reader(open('rsd-subscribers.csv'))

for name, year, email in reader:
    if not email:
        continue
    name = ' '.join(reversed([x.strip() for x in name.split(',', 2)]))
    email += '@swarthmore.edu'
    kind, created = UserKind.objects.get_or_create(kind='s', year=year)

    num_subs= Subscriber.objects.find_by_email(email).filter(receive='i').count()
    if not num_subs:
        try:
            try:
                user = User.objects.get(email=email).get_profile()
            except User.MultipleObjectsReturned:
                user = max(User.objects.filter(email=email), key=lambda s: len(sname)).get_profile()UserKind.objects.get_or_create(kind='s', year=year)
            Subscriber.objects.create(user=user, receive='i')            user.kind = kind            user.save()
        except User.DoesNotExist:
            Subscriber.objects.create(_name=name, _email=email, _kind=kind)
    else:
        for sub in Subscriber.rsd.find_by_email(email):
            if sub.user:                sub.user.kind = kind                sub.user.save()
            else:
                sub._kind = kind
                sub.save()


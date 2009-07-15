#!/usr/bin/evn python

from django.core.management.base import NoArgsCommand
from django.conf import settings
from gazjango.community.sources import *
import logging
import sys
import optparse

class Command(NoArgsCommand):

    log = logging.getLogger('community.retrieve')

    def handle_noargs(self,**options):
        opts=None
        args=None
        
        log.info('starting to update sources')
        sources = settings.AGRO_SETTINGS['source_list']

        if args and len(args) > 1:
            sources = args[1:]
            for source in sources:
                if source not in settings.AGRO_SETTINGS['source_list']:
                    log.warning('%s is not a valid source, removing from update list.', source)
                    sources.remove(source)

        args = {}
        force_run = False
        if hasattr(opts, 'force'):
            if opts.force == True:
                force_run = True

        for s in import_source_modules(source_list=sources, class_name='retrieve'):
            log.info('')
            log.info('trying to update %s', s.__name__)

            base_name = s.__name__[s.__name__.rfind('.')+1:]

            if base_name in settings.AGRO_SETTINGS['api_keys'].keys():
                args['api_key'] = settings.AGRO_SETTINGS['api_keys'][base_name]

            if base_name in settings.AGRO_SETTINGS['accounts'].keys():
                account = settings.AGRO_SETTINGS['accounts'][base_name]
            else:
                log.error('no credentials for %s', base_name)
                continue

            if isinstance(account, (tuple, list)):
                for a in account:
                    args['account'] = a
                    log.info('using %s account: %s', base_name, args['account'])
                    s.retrieve(force_run, **args)
            else:
                args['account'] = account
                log.info('using %s account: %s', base_name, args['account'])
                s.retrieve(force_run, **args)

            log.info('done updating %s', s.__name__)
            log.info('')

from gazjango.options.helpers import header_notices, header_unauth_notice, header_auth_notice

def headerbar(request):
    """Adds header_unauth_notice and header_auth_notice variables to the context."""
    notices = header_notices()
    return { 'header_unauth_notice': header_unauth_notice(notices),
             'header_auth_notice': header_auth_notice(notices) }

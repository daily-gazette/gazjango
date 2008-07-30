import settings

def is_from_swat(user=None, ip=None):
    if user:
        return user.is_from_swat(ip=ip)
    else:
        return ip_from_swat(ip)

def ip_from_swat(ip):
    return ip and ip.startswith(settings.SWARTHMORE_IP_BLOCK)

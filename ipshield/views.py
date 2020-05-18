from django.http import HttpResponse
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta
from .models import Log, Blocked


# block IP when number of events reaches maxAllowed
def add_event(ipAddress, eventName, findTime, maxAllowed):

    now = timezone.now()

    # remove events older than findTime
    dateLim = now - timedelta(minutes=findTime)
    Log.objects.filter(EventName=eventName, EventDate__lt=dateLim).delete()

    # add new entry
    obj = Log(EventName=eventName, IpAddress=ipAddress)
    obj.save()

    # block IP if counted number equals limit
    num = Log.objects.filter(IpAddress=ipAddress, EventName=eventName).count()
    if num >= maxAllowed:
        obj = Blocked.objects.get_or_create(EventName=eventName, IpAddress=ipAddress)[0]
        obj.BlockDate = now
        obj.save()


def is_ip_blocked(ipAddress, eventName, blockTime):
    # remove blocked IPs older than blockTime
    now = timezone.now()
    dateLim = now - timedelta(minutes=blockTime)
    Blocked.objects.filter(EventName=eventName, BlockDate__lt=dateLim).delete()

    # check if any entries are still left
    isBlocked = Blocked.objects.filter(EventName=eventName, IpAddress=ipAddress).exists()

    return isBlocked


# this returns the default lock page
def lock_page():

    html = (
        '<html>'
        '   <head><meta name="viewport" content="width=device-width, initial-scale=1" /></head>'
        '   <body style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 18px;">'
        '      <div>Sorry! Your request has been blocked.</div>'
        '       <a href="/">home</a>'
        '   </body>'
        '</html>'
    )

    return HttpResponse(html, status=429)


# logic will not add events once IP has been blocked
def limit_ips(eventName, blockTime, findTime, maxAllowed, isEvent = lambda request: True, locked_view = lock_page()):
    def real_decorator(viewFunc):
        def wrapper(request, *args, **kwargs):
            # get IP address of remote client

            # -----------------------------------------------------------------------------------------
            # WARNING: You might need to hack this part of the code to get the proper
            # client IP address. The HTTP headers HTTP_X_FORWARDED_FOR and REMOTE_ADDR
            # vary from system to system. See
            #
            #     https://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
            #
            # for a discussion of this issue. Sometimes problems can be solved by replacing
            # 'REMOTE_ADDR' with 'HTTP_X_FORWARDED_FOR'.
            # -----------------------------------------------------------------------------------------

            remoteAddress = request.META.get('REMOTE_ADDR')

            isLocked = False
            if isEvent(request):
                if maxAllowed == 0 or is_ip_blocked(remoteAddress, eventName, blockTime):
                    isLocked = True
                else:
                    add_event(remoteAddress, eventName, findTime, maxAllowed)

            if isLocked:
                result = locked_view
            else:
                result = viewFunc(request, *args, **kwargs)

            return result

        return wrapper
    return real_decorator


def LimitIps_as_view(eventName, blockTime, findTime, maxAllowed, isEvent = lambda request: True, locked_view = lock_page(), **initkwargs):
    """A function that limits the number of page requests by IP address.
    It is to be used in place of function TemplateView.as_view."""
    return limit_ips(eventName, blockTime, findTime, maxAllowed, isEvent, locked_view)(TemplateView.as_view(**initkwargs))


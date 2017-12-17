from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
import datetime
from .models import Log, Blocked


# block IP when number of events reaches maxAllowed
def add_event(ipAddress, eventName, findTime, maxAllowed):

    now = timezone.now()

    # remove events older than findTime
    dateLim = now - datetime.timedelta(minutes=findTime)
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
    dateLim = now - datetime.timedelta(minutes=blockTime)
    Blocked.objects.filter(EventName=eventName, BlockDate__lt=dateLim).delete()

    # check if any entries are still left
    isBlocked = Blocked.objects.filter(EventName=eventName, IpAddress=ipAddress).exists()

    return isBlocked


# this returns the default lock page
def lock_page(request):
    msg = "Sorry! Your request has been blocked."
    html = "".join(("<html><body><h1><center>", msg, "<br><a href=\"/\">home</a></center></h1></body></html>"))
    return HttpResponse(html, status=429)


# logic will not add events once IP has been blocked
def filt_req(eventName, blockTime, findTime, maxAllowed, filtFunc = lambda request: True, lockPageViewFunc = lock_page):
    def real_decorator(viewFunc):
        def wrapper(*args):
            # iterate to make sure that we have found the WSGIRequest object
            for request in args:
                if isinstance (request, WSGIRequest):
                    # get IP address of remote client

                    # NOTE: You might need to hack this part of the code to get the proper
                    # client IP address. The HTTP headers HTTP_X_FORWARDED_FOR and REMOTE_ADDR
                    # vary from system to system.

                    remoteAddress = request.META.get('REMOTE_ADDR')

                    #remoteAddress = request.META.get('HTTP_X_FORWARDED_FOR')
                    #if not remoteAddress:
                        #remoteAddress = request.META.get('REMOTE_ADDR')

                    if is_ip_blocked(remoteAddress, eventName, blockTime):
                        result = lockPageViewFunc(request)
                    else:
                        if filtFunc(request):
                            add_event(remoteAddress, eventName, findTime, maxAllowed)
                        result = viewFunc(*args)
                    return result

        return wrapper
    return real_decorator




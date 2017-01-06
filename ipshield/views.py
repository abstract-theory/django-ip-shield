from django.http import HttpResponse
from django.http import HttpRequest
from django.utils import timezone
import datetime
from .models import Log, Blocked


# block IP when number of events reaches maxAllowed
def add_event(ipAddress, eventName, findTime, maxAllowed):

    # remove events older than findTime
    now = timezone.now()
    dateLim = now - datetime.timedelta(minutes=findTime)
    Log.objects.filter(IpAddress=ipAddress, EventDate__lt=dateLim, EventName=eventName).delete()

    # add new entry
    obj = Log(IpAddress=ipAddress, EventName=eventName)
    obj.save()

    # block IP if counted number equals limit
    num = Log.objects.filter(IpAddress=ipAddress, EventName=eventName).count()
    if num >= maxAllowed:
        # update date of oldest record
        obj = Log.objects.filter(IpAddress=ipAddress, EventName=eventName).order_by('EventDate')[0]
        obj.EventDate = now
        obj.save()

        # add record to banned list, or if it already exists, update the datetime
        obj = Blocked.objects.get_or_create(IpAddress=ipAddress, EventName=eventName)[0]
        obj.BlockDate = now
        obj.save()


def is_ip_blocked(ipAddress, eventName, blockTime):
    # remove blocked IPs older than blockTime
    now = timezone.now()
    dateLim = now - datetime.timedelta(minutes=blockTime)
    Blocked.objects.filter(IpAddress=ipAddress, BlockDate__lt=dateLim, EventName=eventName).delete()

    # check if any entries are still left
    isBlocked = Blocked.objects.filter(IpAddress=ipAddress, EventName=eventName).exists()

    return isBlocked


# logic will not add events once IP has been blocked
# Note: function without an HttpRequest object ought to raise an exception
def filt_req(eventName, blockTime, findTime, maxAllowed, filtFunc = lambda request: True):
    def real_decorator(viewFunc):
        def wrapper(*args):
            # iterate over all arguments to the view function
            for request in args:
                # first make sure that we have found HttpRequest object
                if isinstance (request, HttpRequest):
                    # get IP address of remote client
                    remoteAddress = request.META.get('REMOTE_ADDR')
                    if is_ip_blocked(remoteAddress, eventName, blockTime):
                        result = view_blocked()
                    else:
                        if filtFunc(request):
                            add_event(remoteAddress, eventName, findTime, maxAllowed)
                        result = viewFunc(*args)
                    return result

        return wrapper
    return real_decorator


def view_blocked():
    msg = "Sorry! This page has been locked."
    html = "".join(("<html><body><h1><center>", msg, "</center></h1></body></html>"))
    return HttpResponse(html)

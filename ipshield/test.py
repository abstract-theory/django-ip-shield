
from django.http import HttpResponse
from django.test import TestCase, RequestFactory, Client

from .models import Log, Blocked
from .views import add_event, is_ip_blocked, filt_req

from datetime import timedelta
from django.utils import timezone


ipAddress = "192.1.1.1"
rf = RequestFactory()
req = rf.get('/fake/url', REMOTE_ADDR=ipAddress)
req_env = rf.post('/fake/url', REMOTE_ADDR=ipAddress)


eventName = "test_event"
blockTime = 5
findTime = 3
maxAllowed = 10


# log only post requests as events
def isEvent(request):
    return request.method == 'POST'


# fake view function that restricts only POST requests
@filt_req(eventName, blockTime, findTime, maxAllowed, isEvent)
def fake_view_func_env(request):
    return HttpResponse(status=200)


# fake view function that restricts any type of request
@filt_req(eventName, blockTime, findTime, maxAllowed)
def fake_view_func(request):
    return HttpResponse(status=200)



class IpShieldTests(TestCase):

    def test_funcs(self):

        count = None
        for n in range(maxAllowed*2):
            b1 = is_ip_blocked(ipAddress, eventName, blockTime)
            add_event(ipAddress, eventName, findTime, maxAllowed)
            if b1:
                count = n
                break
        self.assertEqual(maxAllowed, n)



    def test_findTime(self):

        # add max allowed number of events younger than findTime
        for n in range(maxAllowed):
            res = fake_view_func(req)
            # requests are not blocked
            self.assertEqual(res.status_code, 200)

        res = fake_view_func(req)
        # now request should be blocked
        self.assertEqual(res.status_code, 429)


        # remove blocked IP
        Blocked.objects.filter(EventName=eventName, IpAddress=ipAddress).delete()
        # change date of log entries to be older than findTime
        olderDate = timezone.now() - timedelta(minutes=findTime)
        Log.objects.filter(EventName=eventName, IpAddress=ipAddress).update(EventDate=olderDate)
        # new request should not be blocked now
        res = fake_view_func(req)
        # the old log entries should now be cleared, and one new entry added
        self.assertEqual(Log.objects.filter(EventName=eventName, IpAddress=ipAddress).count(), 1)




    def test_blockTime(self):

        # add Blocked entry younger than blockTime
        date = timezone.now()
        obj = Blocked(EventName=eventName, IpAddress=ipAddress, BlockDate=date)
        obj.save()
        res = fake_view_func(req)
        self.assertEqual(res.status_code, 429)

        # change date of Blocked entry to be older than blockTime
        olderDate = timezone.now() - timedelta(minutes=blockTime)
        Blocked.objects.filter(EventName=eventName, IpAddress=ipAddress).update(BlockDate=olderDate)
        res = fake_view_func(req)
        self.assertEqual(res.status_code, 200)



    def test_isEvent(self):

        # these are all non-events and should not trigger blocking
        for n in range(maxAllowed+1):
            res = fake_view_func_env(req)
            self.assertEqual(res.status_code, 200)

        # run the max allowed number of events
        for n in range(maxAllowed):
            res = fake_view_func_env(req_env)
            # requests are not blocked yet
            self.assertEqual(res.status_code, 200)

        res = fake_view_func_env(req_env)
        # now the event should be blocked
        self.assertEqual(res.status_code, 429)

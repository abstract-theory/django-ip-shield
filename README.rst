=========
IP Shield
=========

IP Shield is a Django app that analyzes HTTP requests and returns lock pages to IP addresses that perform suspicious actions. IP Shield is a per-IP-address rate limiter that enforces the limit with a lock out period. IP Shield also allows you to write your own analysis functions, so anything in the HttpRequest object (URL variables, POST data, HTTP headers, etc.) could trigger page locking. The functionality is influenced by the program Fail2Ban.


Quick start
===========


1. Install And Uninstall
------------------------
It is probably easiest to just drop the source folder into your Django project as you would any other Django app. For completeness, the package installation instructions are written below.

build the package:

.. code-block:: sh

    python3 /path/setup.py sdist

install the package:

.. code-block:: sh

    pip3 install --user /path/django-ip-shield-0.1.5.tar.gz

unistall the package:

.. code-block:: sh

    pip3 uninstall django-ip-shield


2. Modify settings.py
---------------------
Add "ipshield" to your INSTALLED_APPS setting:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'ipshield',
    ]


3. Migrate
----------

Apply migrations for IP Shield by running:

.. code-block:: sh

    python3 manage.py migrate


4. Edit A View File
-------------------
In a view file, import the filt_req decorator as shown below.

.. code-block:: python

    from ipshield.views import filt_req

Add the following variables to the file.

.. code-block:: python

    eventName = "example name" # a name for the event which is being monitored
    blockTime  = 2  # minutes that an IP will be blocked
    findTime   = 1  # number of minutes used to calculate the rate
    maxAllowed = 5  # number of events per findTime that will trigger blocking

As shown below, add the decorator above the view function that you wish to protect.

.. code-block:: python

    @filt_req(eventName, blockTime, findTime, maxAllowed)
    def view(request):
        # function body

Reload the page six times in one minute. The page should now be locked for five minutes, and you should see a page reading "Sorry! This page has been locked." The page will automatically unlock after two minutes.


5. Custom Analysis
-------------------------
You may analyze URL variables, POST data, IP address, etc. To do this, you must write a custom analysis function which will determine exactly what IP Sheild will consider to be suspicious. This function will be passed to the decorator. It should accept an HttpRequest object (which is typically named "request" in Django's documentation) as an input, and it should return a boolean value. An example is shown below.

.. code-block:: python

    myFiltFunc = lambda request: request.GET.get('event') == '1'
    @filt_req(eventName, blockTime, findTime, maxAllowed, filtFunc = myFiltFunc)

The above example would block all requests which had the URL GET variable named 'event' that held a value of '1'. For example, the url below would be counted as an event.

.. code-block:: sh

    a-given-url/?event=1

In contrast, the following would NOT be counted as an event.

.. code-block:: sh

    a-given-url/?event=2


As another example, say that we want to monitor POST requests, but not GET requests. This could be implemented with the analysis function below.

.. code-block:: python

    myFiltFunc = lambda request: request.method == 'POST'


6. Custom View Functions
-------------------------
You may also use custom view function. This is useful if you want to return some of the request data to the client, or if you simply wish to use a particular HTML template when a particular event occurs. To do this, you need to write a view function and pass it to the decorator. An example is shown below.

.. code-block:: python

    def view_blocked(request):
        msg = "We're Sorry! You did something that makes us uncomfortable."
        html = "".join(("<html><body><h1><center>", msg, "</center></h1></body></html>"))
        return HttpResponse(html, status=429)

    @filt_req(eventName, blockTime, findTime, maxAllowed, lockPageViewFunc = view_blocked)


7. Caveats
----------

IP Shield makes the below function call.

.. code-block:: python

    request.META.get('REMOTE_ADDR')

Between Django and any upstream servers, ensure that the REMOTE_ADDR header is properly set. Often, the HTTP_X_FORWARDED_FOR header is used in place of REMOTE_ADDR.


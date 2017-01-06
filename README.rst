=========
IP Shield
=========

IP Shield is a simple Django app that analyzes HTTP requests and blocks IP addresses from loading specific URLs if suspicious activity is detected. IP Shield is similar to a rate limiter, except that there is a limit per time window. When the limit is exceeded, the IP address is blocked for a given amount of time. IP Shield is similar to the program Fail2Ban, but with two major differences.::

    1) Rather than analyzing log files, it analyzes HTTP requests (URLs, post data, and HTTP headers).
    2) Rather than firewalling IP addresses, they are blocked from accessing specific URLs.

Detailed documentation is currently NOT available. The "docs" directory is currently empty.


Quick start
===========


1. Install And Uninstall
------------------------
install package

.. code-block:: sh

    pip3 install --user /path/django-ip-shield-0.1.tar.gz

to unistall package run

.. code-block:: sh

    pip3 uninstall django-ip-shield


2. Modify settings.py
---------------------
Add "ipshield" to your INSTALLED_APPS setting like this

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'ipshield',
    ]


3. Migrate
----------
Run `python manage.py migrate to create the ipishield models.


4. Edit A View
--------------
In a view file, import the filt_req decorator as shown below.

.. code-block:: python

    from ipshield.views import filt_req

Add the following variables to the file.

.. code-block:: python

    eventName = "ip-shield demo" # a name for the event which is being monitored
    blockTime  = 2  # minutes that the IP will be blocked
    findTime   = 1  # minutes back in time for which events will be counted
    maxAllowed = 5  # number of events needed to trigger the view to be locked

As shown below, add the decorator above the specific view function you wish to protect.

.. code-block:: python

    @filt_req(eventName, blockTime, findTime, maxAllowed)
    def view(request):
        # function body

Reload the page five times in one minute. After the fifth page load, the page will be locked for five minutes. Additional page loads will be directed to a page reading "Sorry! This page has been locked." The page will automaticall unlock after two minutes.


5. Set A Specialized Rule
-------------------------
You can also set specific rules which determine what actions leads to the blocking of a view function. The rule is determined by a function returning a boolean value, and it is passed to the decorator. The function should accept a WSGIRequest object (which is typically named "request" in Django's documentation). This object contains the URL variables, the post data, and the HTTP headers. An example is shown below.

.. code-block:: python

    filtFunc = lambda request: request.GET.get('event') == '1'
    @filt_req(eventName, blockTime, findTime, maxAllowed, filtFunc)

The above example would block all requests which had the URL get variable equal to '1'. For example if a given url where routed to our view function, then the url below would be counted as an event.

.. code-block:: sh

    a-given-url/?event=1

While the the following would not.

.. code-block:: sh

    a-given-url/?event=2


6. Caveats
----------

IP Shield makes the below function call.

.. code-block:: python

    request.META.get('REMOTE_ADDR')

Ensure that between Django and upstream servers, that the REMOTE_ADDR header is properly set. Often, the HTTP_X_FORWARDED_FOR header is used in place of REMOTE_ADDR.

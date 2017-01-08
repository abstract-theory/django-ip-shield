=========
IP Shield
=========

IP Shield is a simple Django app that analyzes HTTP requests and directs IP addresses to a lock page if they make suspicious requests. IP Shield is a per-IP-address rate limiter that enforces the limit by having a lock out period. IP Shield also allows user-defined analysis functions, so anything in the HttpRequest object (URL variables, POST data, HTTP headers, etc.) could trigger page locking. The functionality is influenced by the program Fail2Ban.


Quick start
===========


1. Install And Uninstall
------------------------
build the package:

.. code-block:: sh

    python3 /path/setup.py sdist

install package:

.. code-block:: sh

    pip3 install --user /path/django-ip-shield-0.1.tar.gz

unistall package:

.. code-block:: sh

    pip3 uninstall django-ip-shield


2. Modify settings.py
---------------------
Add "ipshield" to your INSTALLED_APPS setting like this:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'ipshield',
    ]


3. Migrate
----------
Run "python manage.py migrate" to create the ipishield models.


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
You can also write an analysis function to determine exactly when a view function will be blocked. The function is passed to the decorator. It should accept an HttpRequest object (which is typically named "request" in Django's documentation) as an input, and it should return a boolean value. An example is shown below.

.. code-block:: python

    filtFunc = lambda request: request.GET.get('event') == '1'
    @filt_req(eventName, blockTime, findTime, maxAllowed, filtFunc)

The above example would block all requests which had the URL GET variable equal to '1'. For example, if a given url were routed to a view function, then the url below would be counted as an event.

.. code-block:: sh

    a-given-url/?event=1

In contrast, the following would not be counted as an event.

.. code-block:: sh

    a-given-url/?event=2


6. Caveats
----------

IP Shield makes the below function call.

.. code-block:: python

    request.META.get('REMOTE_ADDR')

Ensure that between Django and upstream servers, that the REMOTE_ADDR header is properly set. Often, the HTTP_X_FORWARDED_FOR header is used in place of REMOTE_ADDR.

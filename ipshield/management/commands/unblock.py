from django.core.management.base import BaseCommand, CommandError
from ipshield.models import Log, Blocked

class Command(BaseCommand):
    """
    Usage:
    ======
        Listing blocks and logs
        -----------------------
        python manage.py unblock --listblocks
        python manage.py unblock --listlogs
        python manage.py unblock --list

        Removing blocks and logs
        ------------------------
        python manage.py unblock all
        python manage.py unblock --ips 127.0.0.1
        python manage.py unblock --events event_name
    """

    help = 'Unblocks IP addresses.'


    def add_arguments(self, parser):

        parser.add_argument(
            '--stat',
            action='store_true',
            help='Display number of logged events and blocked IPs+events.',
        )

        parser.add_argument(
            '--blocks',
            action='store_true',
            help='Display list of all blocked IPS+events.',
        )

        parser.add_argument(
            '--logs',
            action='store_true',
            help='Display list of all logged events.',
        )

        parser.add_argument(
            '--ips',
            nargs='?',
            action='append',
            help='Delete logs and blocks for listed IP addresses.',
        )

        parser.add_argument(
            '--events',
            nargs='?',
            action='append',
            help='Delete logs and blocks for listed events.',
        )

        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete all logs and blocks.',
        )

    def success(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))


    def handle(self, *args, **options):

        if options['stat']:
            l = Log.objects.all()
            b = Blocked.objects.all()
            self.success(' %d events in log.' % l.count())
            self.success(' %d IP+events in block list.' % b.count())

        elif options['blocks']:
            self.success('Blocked IPs + Events:')
            b = Blocked.objects.all()
            for B in b.values():
                print('    "%s", "%s", "%s"' % (B.get('IpAddress'), B.get('EventName'), B.get('BlockDate')))

        elif options['logs']:
            self.success('Logged events:')
            l = Log.objects.all()
            for L in l.values():
                print('    "%s", "%s", "%s"' % (L.get('IpAddress'), L.get('EventName'), L.get('EventDate')))

        elif options['ips']:
            for ipAddress in options['ips']:
                self.success('IP Address "%s":' % ipAddress)
                l = Log.objects.filter(IpAddress=ipAddress)
                b = Blocked.objects.filter(IpAddress=ipAddress)
                self.success('    %d logged events removed.' % l.count())
                self.success('    %d blocked events removed.' % b.count())
                l.delete()
                b.delete()

        elif options['events']:
            for eventName in options['events']:
                self.success('Event name "%s":' % eventName)
                l = Log.objects.filter(EventName=eventName)
                b = Blocked.objects.filter(EventName=eventName)
                self.success('    %d logged IPs removed.' % l.count())
                self.success('    %d blocked IPs removed.' % b.count())
                l.delete()
                b.delete()

        elif options['all']:
            l = Log.objects.all()
            b = Blocked.objects.all()
            self.success('Removing %d entries from log.' % l.count())
            self.success('Removing %d entries from block list.' % b.count())
            l.delete()
            b.delete()

        else:
            print('Add "--help" argument for command info.')



        # # To do:
        # #   display some more data
        # #
        # elif options['ips']:
            # for ipAddress in options['ips']:
                # self.success('IP Address "%s":' % ipAddress)
                # l = Log.objects.filter(IpAddress=ipAddress)
                # b = Blocked.objects.filter(IpAddress=ipAddress)

                # ld = l.values_list('EventName', flat=True).distinct()
                # ls = list(ld) or None

                # bd = b.values_list('EventName', flat=True).distinct()
                # bs = list(bd) or None

                # self.success('    Events found: %s' % ls)
                # self.success('    %d logged events removed.' % l.count())

                # self.success('    Blocks found: %s' % bs)
                # self.success('    %d blocked events removed.' % b.count())

                # l.delete()
                # b.delete()


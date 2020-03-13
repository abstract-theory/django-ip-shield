from django.core.management.base import BaseCommand, CommandError
from ipshield.models import Log, Blocked

class Command(BaseCommand):
    """
    Usage:
    ======
        Listing blocks and logs
        -----------------------
        django-admin unblock --list
        django-admin unblock --log
        django-admin unblock --block

        Removing blocks and logs
        ------------------------
        django-admin unblock --rmip <IP_Address>
        django-admin unblock --rmevent <Event_Name>
        django-admin unblock --rmall
    """

    help = 'Django management commands for django-ip-shield.'


    def add_arguments(self, parser):

        parser.add_argument(
            '--list',
            action='store_true',
            help='List number of logged events and blocked IPs+events.',
        )

        parser.add_argument(
            '--block',
            action='store_true',
            help='List of all blocked IPS+events.',
        )

        parser.add_argument(
            '--log',
            action='store_true',
            help='List of all logged events.',
        )

        parser.add_argument(
            '--rmip',
            nargs='+',
            action='append',
            help='Remove logs and blocks for listed IP addresses.',
        )

        parser.add_argument(
            '--rmevent',
            nargs='+',
            action='append',
            help='Remove logs and blocks for listed events.',
        )

        parser.add_argument(
            '--rmall',
            action='store_true',
            help='Remove all logs and blocks.',
        )


    def success(self, msg):
        self.stdout.write(self.style.SUCCESS(msg))


    def handle(self, *args, **options):

        if options['list']:
            l = Log.objects.all()
            b = Blocked.objects.all()
            self.success(' %d events in log.' % l.count())
            self.success(' %d IP+events in block list.' % b.count())

        elif options['block']:
            self.success('Blocked IPs + Events:')
            b = Blocked.objects.all()
            for B in b.values():
                print('    "%s", "%s", "%s"' % (B.get('IpAddress'), B.get('EventName'), B.get('BlockDate')))

        elif options['log']:
            self.success('Logged events:')
            l = Log.objects.all()
            for L in l.values():
                print('    "%s", "%s", "%s"' % (L.get('IpAddress'), L.get('EventName'), L.get('EventDate')))

        elif options['rmip']:
            for addresses in options['rmip']:
                for ip in addresses:
                    self.success('IP Address "%s":' % ip)
                    l = Log.objects.filter(IpAddress=ip)
                    b = Blocked.objects.filter(IpAddress=ip)
                    self.success('    %d logged events removed.' % l.count())
                    self.success('    %d blocked events removed.' % b.count())
                    l.delete()
                    b.delete()

        elif options['rmevent']:
            for events in options['rmevent']:
                for ev in events:
                    self.success('Event name "%s":' % ev)
                    l = Log.objects.filter(EventName=ev)
                    b = Blocked.objects.filter(EventName=ev)
                    self.success('    %d logged IPs removed.' % l.count())
                    self.success('    %d blocked IPs removed.' % b.count())
                    l.delete()
                    b.delete()

        elif options['rmall']:
            l = Log.objects.all()
            b = Blocked.objects.all()
            self.success('Removing %d entries from log.' % l.count())
            self.success('Removing %d entries from block list.' % b.count())
            l.delete()
            b.delete()

        else:
            print('Add "--help" argument for command info.')





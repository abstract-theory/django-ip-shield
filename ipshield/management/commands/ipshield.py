from django.core.management.base import BaseCommand
from django.utils import timezone

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

        # subparsers = parser.add_subparsers()

        # add_p = subparsers.add_parser('add')
        # add_p.add_argument("name")
        # add_p.add_argument("--web_port")
        # ...

        # rm = subparsers.add_parser('rm')
        # rm.add_argument("-ip", type=str)
        # rm.add_argument("-event", type=str)

        # rm.add_argument("all", action='store_true')
        # add = subparsers.add_parser('-add')

        # ls = subparsers.add_parser('-list')
        # ls.add_argument("log", nargs='+')
        # ls.add_argument("block", nargs='+')



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
            '--addip',
            nargs=2,
            action='append',
            help='Adds IP with event to block list.',
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

        # print(args)
        # print(options)

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

        elif options['addip']:
            for ip_event in options['addip']:
                ipAddress = ip_event[0]
                eventName = ip_event[1]
                now = timezone.now()
                obj = Blocked.objects.get_or_create(EventName=eventName, IpAddress=ipAddress)[0]
                obj.BlockDate = now
                obj.save()


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





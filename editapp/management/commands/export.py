# command line zone exporter

from django.core.management.base import BaseCommand
from django.db.models import F
from editapp.models import Domain
from time import time
from django.utils.timezone import now
import re

class Command(BaseCommand):
    help = 'Export updated zone files'

    def add_arguments(self, parser):
        parser.add_argument('--updated', type=str, help="Export updated zones to this directory")
        parser.add_argument('--all', type=str, help="Export all zones to this directory")
        parser.add_argument('--list', type=str, help="Export list of zones to this file")
        
    def handle(self, *args, **options):
        """
        do export
        """

        v = options['verbosity']        # 0 - 3, default 1

        if options['list']:
            doms = Domain.objects.all().order_by('domain')
            with open(options['list'], "w") as fo:
                for d in doms:
                    if d.domain != 'HEAD':
                        print(d.domain, file=fo)
                    
        def writeit(doms, dir, head):
            """
            write the domains in doms to files in the dir
            prefix with head if defined
            """
            for d in doms:
                filename = "{0}/{1}".format(dir, d.domain)
                if v > 0:
                    print("export",filename)
                with open(filename, "w") as fo:
                    if head:
                        print(head, file=fo)
                    print(d.rrs, file=fo)
                d.exported = current_time    # mark as exported
                d.save()

        # TZ aware version of "now"
        current_time = now()

        # get the common head records if any
        if options['updated'] or options['all']:
            h = Domain.objects.filter(domain='HEAD')
            if len(h) > 0:
                head = h[0].rrs
                # hack: replace the sequence number with the current
                # timestamp
                timestamp = str(int(time()))
                if v > 0:
                    print("timestamp",timestamp)
                head = re.sub(r'(SOA\s+\S+\s+\S+\s+)\d+', lambda m: m.group(1)+timestamp, head, flags=re.I)
                if v > 1:
                    print("zone head\n", head)
            else:
                head = None
            
        if options['updated']:
            doms = Domain.objects.filter(updated__gt=F('exported')).exclude(domain='HEAD')
            writeit(doms, options['updated'], head)
            if v > 0:
                print("wrote updated zones")

        if options['all']:
            doms = Domain.objects.exclude(domain='HEAD')
            writeit(doms, options['all'], head)
            if v > 0:
                print("wrote all zones")

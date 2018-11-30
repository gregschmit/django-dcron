from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from dcron import models

class Command(BaseCommand):
    """
    The :code:`dcron_run` management command.
    """
    help = 'Run the `dcron` engine.'

    def handle(self, *args, **options):
        """
        Run the auto-discovery process and then invoke each
        :code:`DynamicCronJob`.
        """
        models.DynamicCronJob.discover()
        for i in models.DynamicCronJob.objects.filter(active=True):
            i.run()

from croniter import croniter
from datetime import datetime
import django.apps
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.utils import timezone
import subprocess


def pattern_validator(pattern):
    """
    Validates a pattern and returns a tuple containing a :code:`boolean`
    confirming if the pattern is valid, and a :code:`datetime` object that
    specifies the next time the job should run.
    """
    valid = True
    nexts = []
    for p in pattern.split(';'):
        if not croniter.is_valid(p):
            valid = False
            return (False, None)
        c = croniter(p.strip(), timezone.localtime(timezone.now()))
        nexts.append(c.get_next(datetime))
    nexts.sort()
    return (valid, nexts[0])


class DynamicCronJob(models.Model):
    """
    Corresponds to either a model class (where the :code:`instance_id` field is
    0), or a model instance (where the :code:`instance_id` field is nonzero).
    """
    instance_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    instance_id = models.PositiveIntegerField(null=True)
    instance = GenericForeignKey('instance_type', 'instance_id')
    enabled = models.BooleanField(default=True)
    next_run = models.DateTimeField(blank=True, null=True, editable=False)
    resolved_pattern = models.CharField(max_length=255, blank=True, editable=False)
    last_resolved = models.DateTimeField(blank=True, null=True, editable=False)

    def __str__(self):
        if self.instance_id:
            return self.instance_model + " :: {0}".format(self.instance_id)
        return self.instance_model

    @property
    def instance_model(self):
        return "{0} :: {1}".format(self.instance_type.app_label, self.instance_type)

    @classmethod
    def discover(cls):
        """
        Tterates over the available models (and instances) and registers them
        as :code:`DynamicCronJob` models if they implement the proper
        attributes.
        """
        jobs = list(cls.objects.all())
        for m in django.apps.apps.get_models():
            if hasattr(m, 'dcron_class_pattern'):
                x = cls.objects.filter(instance_type=ContentType.objects.get_for_model(m), instance_id=0).first()
                if x:
                    x.resolve()
                    jobs.remove(x)
                else:
                    x = DynamicCronJob()
                    x.instance_type = ContentType.objects.get_for_model(m)
                    x.instance_id = 0
                    x.save()
                    x.resolve()
            if hasattr(m, 'dcron_pattern'):
                for i in m.objects.all():
                    x = cls.objects.filter(instance_type=ContentType.objects.get_for_model(i), instance_id=i.id).first()
                    if x:
                        x.resolve()
                        jobs.remove(x)
                    else:
                        x = DynamicCronJob()
                        x.instance = i
                        x.save()
                        x.resolve()
        for j in jobs:
            j.delete()

    def resolve(self):
        """
        Checks to see if the target class/object has a valid cron pattern,
        updates the enabled status, and also updates the :code:`next_run` value.
        """
        if self.instance_id == 0:
            try:
                pattern = self.instance_type.model_class().dcron_class_pattern()
            except TypeError:
                pattern = self.instance_type.model_class().dcron_class_pattern
        else:
            try:
                pattern = self.instance.dcron_pattern()
            except TypeError:
                pattern = self.instance.dcron_pattern
        # if pattern changed, reset everything
        if self.resolved_pattern != pattern:
            self.next_run = None
            self.resolved_pattern = ''
        # if we have resolved_pattern, do nothing
        # else, check validity, resolve and set next
        if not self.resolved_pattern:
            valid, next_run = pattern_validator(pattern)
            if valid:
                self.next_run = next_run
                self.resolved_pattern = pattern
        self.last_resolved = timezone.now()
        self.save()

    def is_due(self):
        """
        Determines if this job is due to be run.
        """
        if not self.next_run or self.next_run <= timezone.now():
            return True
        return False

    def run(self):
        """
        If enabled and we are due for the next run, update the next_run and
        execute the model's :code:`dcron_run` or :code:`dcron_class_run` method.
        """
        if not self.is_due(): return
        if self.instance_id == 0:
            obj = self.instance_type.model_class()
        else:
            obj = self.instance
        valid, next_run = pattern_validator(self.resolved_pattern)
        if valid:
            self.next_run = next_run
        self.save()
        # if enabled, try running
        if not self.enabled:
            return
        if self.instance_id:
            if hasattr(obj, 'dcron_run') and callable(obj.dcron_run):
                obj.dcron_run()
                l = Log(job=self, msg="Success - `dcron_run` called".format(self.id))
                l.save()
            elif hasattr(obj, 'run') and callable(obj.run):
                obj.run()
                l = Log(job=self, msg="Success - `run()` called")
                l.save()
            else:
                l = Log(job=self, msg="Failure - No `dcron_run()` or `run()` method")
                l.save()
        else:
            if hasattr(obj, 'dcron_class_run') and callable(obj.dcron_class_run):
                obj.dcron_class_run()
                l = Log(job=self, msg="Success - `dcron_class_run()` called")
                l.save()
            elif hasattr(obj, 'run') and callable(obj.run):
                obj.run()
                l = Log(job=self, msg="Success - `run()` called")
                l.save()
            else:
                l = Log(job=self, msg="Failure - No `dcron_class_run()` or `run()` method")
                l.save()


class Log(models.Model):
    """
    Store logs.
    """
    job = models.ForeignKey(DynamicCronJob, on_delete=models.CASCADE, blank=True, null=True)
    msg = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class ScheduledManagementCommand(models.Model):
    """
    Example implementation of scheduling a management command to be run
    periodically.
    """
    enabled = models.BooleanField(default=True)
    cron_schedule = models.CharField(default='* * * * *', max_length=255, blank=True)
    management_command = models.CharField(default='test', max_length=255)

    def dcron_pattern(self):
        if not self.enabled: return ''
        return self.cron_schedule

    def run(self):
        call_command(self.management_command)


class ScheduledShellCommand(models.Model):
    """
    Example implementation of scheduling a shell command to be run
    periodically.
    """
    enabled = models.BooleanField(default=True)
    cron_schedule = models.CharField(default='* * * * *', max_length=255, blank=True)
    shell_command = models.CharField(max_length=255)

    def dcron_pattern(self):
        if not self.enabled: return ''
        return self.cron_schedule

    def run(self):
        subprocess.check_output(self.shell_command, shell=True)

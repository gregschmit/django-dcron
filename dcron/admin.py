from django.contrib import admin
from . import models


class DynamicCronJobAdmin(admin.ModelAdmin):
    list_filter = ('enabled', 'instance_type__app_label')
    list_display = ('__str__', 'enabled', 'next_run', 'resolved_pattern', 'last_resolved')
    search_fields = list_display
    readonly_fields = ('__str__', 'next_run', 'resolved_pattern', 'last_resolved')
    fieldsets = (
            (None, { 'fields': ('enabled',)}),
            ('Readonly', { 'fields':(*readonly_fields,)}),
            )

    def get_queryset(self, request):
        models.DynamicCronJob.discover()
        query = super().get_queryset(request)
        return query


class LogAdmin(admin.ModelAdmin):
    list_filter = ('job',)
    list_display = ('id',) + list_filter + ('msg', 'created', 'updated')
    search_fields = list_display
    fields = ('job', 'msg',)


class ScheduledManagementCommandAdmin(admin.ModelAdmin):
    list_filter = ('enabled', 'cron_schedule')
    list_display = ('id',) + list_filter + ('management_command',)
    search_fields = list_display
    fields = ('enabled', 'cron_schedule', 'management_command',)


class ScheduledShellCommandAdmin(admin.ModelAdmin):
    list_filter = ('enabled', 'cron_schedule')
    list_display = ('id',) + list_filter + ('shell_command',)
    search_fields = list_display
    fields = ('enabled', 'cron_schedule', 'shell_command',)


admin.site.register(models.DynamicCronJob, DynamicCronJobAdmin)
admin.site.register(models.Log, LogAdmin)
admin.site.register(models.ScheduledManagementCommand, ScheduledManagementCommandAdmin)
admin.site.register(models.ScheduledShellCommand, ScheduledShellCommandAdmin)

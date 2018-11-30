from django.contrib import admin
from . import models


class DynamicCronJobAdmin(admin.ModelAdmin):
    list_filter = ('active', 'instance_type', 'instance_id')
    list_display = ('id',) + list_filter + ('next_run', 'resolved_pattern', 'last_resolved')
    search_fields = list_display
    readonly_fields = ('id', 'instance_type', 'instance_id', 'next_run', 'resolved_pattern', 'last_resolved')
    fieldsets = (
            (None, { 'fields': ('active',)}),
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
    list_filter = ('dcron_pattern', 'dcron_enable')
    list_display = ('id',) + list_filter + ('management_command',)
    search_fields = list_display
    fields = ('dcron_pattern', 'dcron_enable', 'management_command',)


class ScheduledShellCommandAdmin(admin.ModelAdmin):
    list_filter = ('dcron_pattern', 'dcron_enable')
    list_display = ('id',) + list_filter + ('shell_command',)
    search_fields = list_display
    fields = ('dcron_pattern', 'dcron_enable', 'shell_command',)


admin.site.register(models.DynamicCronJob, DynamicCronJobAdmin)
admin.site.register(models.Log, LogAdmin)
admin.site.register(models.ScheduledManagementCommand, ScheduledManagementCommandAdmin)
admin.site.register(models.ScheduledShellCommand, ScheduledShellCommandAdmin)

from django.contrib import admin

from .models import Robot


@admin.register(Robot)
class RobotAdmin(admin.ModelAdmin):
    list_display = ('serial', 'model', 'version', 'created', 'id')
    list_filter = ('model', 'version', 'created')
    search_fields = ('serial', 'model', 'version')
    fields = ('model', 'version', 'created')
    readonly_fields = ('serial',)
    ordering = ('serial',)
    list_per_page = 20
    date_hierarchy = 'created'

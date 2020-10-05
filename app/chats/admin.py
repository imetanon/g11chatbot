from django.contrib import admin
from .models import Log


class LogAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    # list_display = ('name', 'location', 'created_at', 'updated_at')

admin.site.register(Log, LogAdmin)


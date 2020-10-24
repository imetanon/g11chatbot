from django.contrib import admin
from .models import TripPlan


class TripPlanAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(TripPlan, TripPlanAdmin)


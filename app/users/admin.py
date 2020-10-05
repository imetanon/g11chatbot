from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')

    # fieldsets = [
    #     ('Created Information', {'fields': ['created_at', 'updated_at']}),
    # ]


admin.site.register(User, UserAdmin)

from django.contrib import admin
from .models import Place, BusinessHour, Category, SubCategory, PlaceAction, SubCategoryKeyword


class PlaceAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('name', 'location', 'created_at', 'updated_at')
    # fields = ('name', 'location', 'created_at', 'updated_at')

    # fieldsets = [
    #     ('Created Information', {'fields': ['created_at', 'updated_at']}),
    # ]
    
class PlaceActionAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('user', 'place', 'action', 'updated_at')


admin.site.register(Place, PlaceAdmin)
admin.site.register(BusinessHour)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(PlaceAction, PlaceActionAdmin)
admin.site.register(SubCategoryKeyword)

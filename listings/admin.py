from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 0

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'city', 'price_per_night', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'city', 'country', 'created_at')
    search_fields = ('title', 'address', 'city', 'owner__username')
    ordering = ('-created_at',)
    inlines = [PropertyImageInline]

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'uploaded_at', 'is_primary')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('property__title',)

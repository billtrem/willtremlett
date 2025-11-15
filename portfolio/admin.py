from django.contrib import admin
from .models import SiteSettings, ContactMethod, YearTab, Project


class ContactInline(admin.TabularInline):
    model = ContactMethod
    extra = 1


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    inlines = [ContactInline]

    def has_add_permission(self, request):
        # Only allow ONE site settings object
        return not SiteSettings.objects.exists()


class ProjectInline(admin.StackedInline):
    model = Project
    extra = 1


@admin.register(YearTab)
class YearTabAdmin(admin.ModelAdmin):
    list_display = ("label", "year", "order")
    ordering = ("order", "-year")
    inlines = [ProjectInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "year_tab", "role", "content_length", "order")
    list_filter = ("year_tab", "role")
    search_fields = ("title", "description")

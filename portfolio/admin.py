from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, ContactMethod, YearTab, Project, ProjectBlock


class ContactMethodInline(admin.TabularInline):
    model = ContactMethod
    extra = 0
    fields = ("label", "email", "order")
    ordering = ("order", "label")


class ProjectBlockInline(admin.TabularInline):
    """
    Lets you build a Project like:
    image -> text -> embed -> text -> image ...
    """
    model = ProjectBlock
    extra = 0
    ordering = ("order", "id")

    fields = (
        "order",
        "block_type",
        "text",
        "image",
        "embed_url",
        "embed_preview",
    )

    readonly_fields = ("embed_preview",)

    def embed_preview(self, obj: ProjectBlock):
        """
        For EMBED blocks, show the resolved iframe src link (YouTube/Vimeo).
        """
        if not obj or not obj.embed_url:
            return "—"

        src = obj.get_embed_src()
        if not src:
            return "Could not detect provider (use a normal YouTube/Vimeo link)."

        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a>',
            src,
            src,
        )
    embed_preview.short_description = "Embed preview URL"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("display_name",)
    inlines = [ContactMethodInline]


@admin.register(YearTab)
class YearTabAdmin(admin.ModelAdmin):
    list_display = ("label", "year", "order")
    list_editable = ("order",)
    search_fields = ("label",)
    ordering = ("order", "-year")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "role",
        "order",
        "year_tab",
        "has_blocks_display",
        "has_video_display",
    )
    list_filter = ("category", "year_tab")
    search_fields = ("title", "role", "description")
    list_editable = ("order",)
    ordering = ("category", "order", "title")

    inlines = [ProjectBlockInline]

    readonly_fields = ("embed_preview",)

    fieldsets = (
        ("Category", {
            "fields": ("category", "order", "year_tab")
        }),
        ("Core details", {
            "fields": ("title", "content_length", "role", "description", "image")
        }),
        ("Video (optional)", {
            "description": (
                "Paste a normal YouTube or Vimeo URL. The site will automatically embed it. "
                "For Art, you will usually add EMBED blocks below instead."
            ),
            "fields": ("video_embed_url", "embed_preview"),
        }),
    )

    def has_video_display(self, obj: Project) -> str:
        return "Yes" if obj.has_video else "—"
    has_video_display.short_description = "Has video"

    def has_blocks_display(self, obj: Project) -> str:
        return "Yes" if obj.has_blocks else "—"
    has_blocks_display.short_description = "Has blocks"

    def embed_preview(self, obj: Project):
        """
        Shows what iframe src we will generate from the Project video URL.
        Useful for debugging embed issues.
        """
        if not obj.video_embed_url:
            return "—"

        src = obj.get_embed_src()
        if not src:
            return "Could not detect provider (use a normal YouTube/Vimeo link)."

        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a>',
            src,
            src,
        )
    embed_preview.short_description = "Embed preview URL"

from django.db import models


class SiteSettings(models.Model):
    """
    Global site content for Will Tremlett.
    """
    display_name = models.CharField(max_length=200, default="Will Tremlett")
    tagline = models.CharField(max_length=255, blank=True)
    bio = models.TextField(help_text="Your director biography.")

    hero_image = models.ImageField(
        upload_to="willtremlett/hero/",
        blank=True,
        null=True,
        help_text="Upload a hero image (stored via Cloudinary)."
    )

    mailchimp_embed_code = models.TextField(
        blank=True,
        help_text="Paste your Mailchimp form HTML embed code here."
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site Settings"


class ContactMethod(models.Model):
    """
    e.g. Press – press@willtremlett.com
    """
    site = models.ForeignKey(
        SiteSettings,
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    label = models.CharField(max_length=100)
    email = models.EmailField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "label"]

    def __str__(self):
        return f"{self.label}: {self.email}"


class YearTab(models.Model):
    """
    Left-hand-year navigation tab.
    """
    year = models.PositiveIntegerField()
    label = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-year"]

    def __str__(self):
        return self.label or str(self.year)


class Project(models.Model):
    """
    A project for a given year tab.
    """
    year_tab = models.ForeignKey(
        YearTab,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    title = models.CharField(max_length=255)
    content_length = models.CharField(max_length=100)
    role = models.CharField(max_length=100, help_text="Director, Producer, etc.")
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="willtremlett/projects/",
        blank=True,
        null=True,
        help_text="Project still/poster image (Cloudinary)."
    )

    video_embed_url = models.URLField(
        blank=True,
        help_text="Paste a YouTube or Vimeo embed URL."
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

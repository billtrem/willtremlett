from django.db import models
from django.core.exceptions import ValidationError
from urllib.parse import urlparse, parse_qs


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
    Legacy structure (kept for backwards compatibility).
    """
    year = models.PositiveIntegerField()
    label = models.CharField(max_length=50, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-year"]

    def __str__(self):
        return self.label or str(self.year)


def _embed_src_from_url(url: str) -> str:
    """
    Convert common YouTube/Vimeo URLs into an embeddable iframe src.
    Returns "" if it can't detect a supported provider.
    """
    if not url:
        return ""

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception:
        return ""

    host = (parsed.netloc or "").lower().replace("www.", "")
    path = (parsed.path or "").strip("/")

    # --- YouTube ---
    # youtu.be/<id>
    if host == "youtu.be":
        video_id = path.split("/")[0] if path else ""
        return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1" if video_id else ""

    # youtube.com/watch?v=<id>
    # youtube.com/embed/<id>
    # youtube.com/shorts/<id>
    if host in ("youtube.com", "m.youtube.com", "music.youtube.com"):
        if path.startswith("watch"):
            qs = parse_qs(parsed.query or "")
            video_id = (qs.get("v") or [""])[0]
            return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1" if video_id else ""

        if path.startswith("embed/"):
            video_id = path.split("embed/", 1)[1].split("/")[0]
            return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1" if video_id else ""

        if path.startswith("shorts/"):
            video_id = path.split("shorts/", 1)[1].split("/")[0]
            return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1" if video_id else ""

    # --- Vimeo ---
    # vimeo.com/<id>
    # player.vimeo.com/video/<id>
    if host == "vimeo.com":
        video_id = path.split("/")[0] if path else ""
        return f"https://player.vimeo.com/video/{video_id}" if video_id.isdigit() else ""

    if host == "player.vimeo.com":
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "video" and parts[1].isdigit():
            return f"https://player.vimeo.com/video/{parts[1]}"
        return ""

    return ""


class Project(models.Model):
    """
    A project entry (Film / Video / Art).
    """

    class Category(models.TextChoices):
        FILMS = "films", "Films"
        VIDEO = "video", "Video"
        ART = "art", "Art"

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.FILMS,
        db_index=True,
    )

    # Legacy field (optional)
    year_tab = models.ForeignKey(
        YearTab,
        on_delete=models.SET_NULL,
        related_name="projects",
        blank=True,
        null=True,
    )

    title = models.CharField(max_length=255)

    # Make these optional so Art doesn’t feel forced
    content_length = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=100, blank=True, help_text="Director, Producer, etc. (optional for Art)")

    # Short description / intro (still useful on tiles or if no blocks exist)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="willtremlett/projects/",
        blank=True,
        null=True,
        help_text="Project still/poster image (Cloudinary)."
    )

    # URL-only workflow (long enough for params)
    video_embed_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="Paste a normal YouTube/Vimeo URL (e.g. https://youtu.be/ID or https://vimeo.com/ID)."
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_embed_src(self) -> str:
        return _embed_src_from_url(self.video_embed_url)

    @property
    def has_video(self) -> bool:
        return bool(self.get_embed_src())

    @property
    def has_blocks(self) -> bool:
        # related_name="blocks" below
        return self.blocks.exists()


class ProjectBlock(models.Model):
    """
    An ordered content block for a Project.
    This enables Art (and any project) to be built like:
    image -> text -> embed -> text -> image ...
    """

    class BlockType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        EMBED = "embed", "Embed (YouTube/Vimeo)"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="blocks",
    )

    block_type = models.CharField(
        max_length=20,
        choices=BlockType.choices,
        default=BlockType.TEXT,
        db_index=True,
    )

    # TEXT
    text = models.TextField(blank=True)

    # IMAGE
    image = models.ImageField(
        upload_to="willtremlett/project_blocks/",
        blank=True,
        null=True,
        help_text="Image block (Cloudinary)."
    )

    # EMBED
    embed_url = models.URLField(
        blank=True,
        max_length=500,
        help_text="Paste a normal YouTube/Vimeo URL."
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.project.title} — {self.block_type} #{self.order}"

    def clean(self):
        """
        Lightweight validation so the admin behaves nicely:
        - TEXT blocks should have text
        - IMAGE blocks should have an image
        - EMBED blocks should have an embed_url that we can parse
        """
        if self.block_type == self.BlockType.TEXT:
            if not (self.text or "").strip():
                raise ValidationError({"text": "Text block requires text."})

        elif self.block_type == self.BlockType.IMAGE:
            if not self.image:
                raise ValidationError({"image": "Image block requires an image."})

        elif self.block_type == self.BlockType.EMBED:
            if not (self.embed_url or "").strip():
                raise ValidationError({"embed_url": "Embed block requires a URL."})
            if not self.get_embed_src():
                raise ValidationError({"embed_url": "Enter a valid YouTube or Vimeo URL."})

    def get_embed_src(self) -> str:
        return _embed_src_from_url(self.embed_url)

    @property
    def has_embed(self) -> bool:
        return bool(self.get_embed_src())

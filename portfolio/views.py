from django.shortcuts import render, get_object_or_404, redirect
from .models import SiteSettings, Project


def films(request):
    site = SiteSettings.objects.first()
    projects = (
        Project.objects
        .filter(category=Project.Category.FILMS)
        .order_by("order", "title")
    )
    return render(request, "portfolio/films.html", {
        "site": site,
        "projects": projects,
        "current_section": "films",
        "page_title": "Films",
    })


def video(request):
    site = SiteSettings.objects.first()
    projects = (
        Project.objects
        .filter(category=Project.Category.VIDEO)
        .order_by("order", "title")
    )
    return render(request, "portfolio/video.html", {
        "site": site,
        "projects": projects,
        "current_section": "video",
        "page_title": "Video",
    })


def art(request):
    site = SiteSettings.objects.first()
    projects = (
        Project.objects
        .filter(category=Project.Category.ART)
        .order_by("order", "title")
    )
    return render(request, "portfolio/art.html", {
        "site": site,
        "projects": projects,
        "current_section": "art",
        "page_title": "Art",
    })


def project_detail(request, pk: int):
    """
    Default detail page for Films + Video.
    If the project is Art, send to the Art detail page instead.
    """
    project = get_object_or_404(Project, pk=pk)

    if project.category == Project.Category.ART:
        return redirect("art_detail", pk=project.pk)

    site = SiteSettings.objects.first()
    return render(request, "portfolio/project_detail.html", {
        "site": site,
        "project": project,
        "current_section": project.category,
    })


def art_detail(request, pk: int):
    """
    Art detail page renders the block-based builder content.
    """
    site = SiteSettings.objects.first()
    project = (
        Project.objects
        .prefetch_related("blocks")
        .get(pk=pk, category=Project.Category.ART)
    )

    return render(request, "portfolio/art_detail.html", {
        "site": site,
        "project": project,
        "current_section": "art",
    })

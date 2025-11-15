from django.shortcuts import render
from .models import SiteSettings, YearTab


def home(request):
    site = SiteSettings.objects.first()
    tabs = YearTab.objects.prefetch_related("projects").all()

    selected_year_id = request.GET.get("year")
    if selected_year_id:
        try:
            selected_tab = tabs.get(id=selected_year_id)
        except YearTab.DoesNotExist:
            selected_tab = tabs.first()
    else:
        selected_tab = tabs.first()

    return render(request, "portfolio/home.html", {
        "site": site,
        "year_tabs": tabs,
        "selected_year": selected_tab,
    })

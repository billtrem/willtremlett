from django.urls import path
from . import views

urlpatterns = [
    path("", views.films, name="home"),
    path("films/", views.films, name="films"),
    path("video/", views.video, name="video"),
    path("art/", views.art, name="art"),

    # NEW: tile click -> detail page
    path("work/<int:pk>/", views.project_detail, name="project_detail"),
    path("art/<int:pk>/", views.art_detail, name="art_detail"),

]

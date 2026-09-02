from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("course/create/", views.create_course, name="create_course"),
    path("course/<int:pk>/", views.course_detail, name="course_detail"),
    path("course/<int:pk>/enroll/", views.enroll_course, name="enroll_course"),
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Scraper API Route
    path(
        "api/scraper/radioechoes/",
        views.radioechoes_scraper_api,
        name="radioechoes_scraper",
    ),
]
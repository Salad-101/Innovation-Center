from pathlib import Path

from django.contrib import admin
from django.http import FileResponse
from django.urls import include, path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR.parent / "frontend" / "dist"


def frontend(request):
    return FileResponse(
        open(FRONTEND_DIST / "index.html", "rb"),
        content_type="text/html",
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("ideas.urls")),
    path("", frontend),
]
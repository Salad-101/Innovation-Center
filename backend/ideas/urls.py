from django.urls import path

from .views import (
    IdeaListCreateAPIView,
    IdeaDetailAPIView,
    ArchiveIdeaAPIView,
    UnarchiveIdeaAPIView,
    StudentListCreateAPIView,
    StudentDetailAPIView,
    MeetingListCreateAPIView,
    MeetingDetailAPIView,
)


urlpatterns = [
    # Ideas
    path("ideas/", IdeaListCreateAPIView.as_view(),),
    path("ideas/<int:pk>/", IdeaDetailAPIView.as_view(),),
    path("ideas/<int:pk>/archive/", ArchiveIdeaAPIView.as_view(),),
    path("ideas/<int:pk>/unarchive/", UnarchiveIdeaAPIView.as_view()),

    # Students
    path("students/", StudentListCreateAPIView.as_view(),),
    path("students/<int:pk>/", StudentDetailAPIView.as_view(),),

    # Meetings
    path("meetings/", MeetingListCreateAPIView.as_view(),),
    path("meetings/<int:pk>/", MeetingDetailAPIView.as_view(),),
]

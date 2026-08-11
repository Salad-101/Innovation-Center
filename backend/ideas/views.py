from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Idea, Student, Meeting
from .serializers import (
    IdeaSerializer,
    StudentSerializer,
    MeetingSerializer,
)

# Idea APIs
class IdeaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = IdeaSerializer

    def get_queryset(self):
        queryset = Idea.objects.filter(is_archived=False)

        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(status=status)

        return queryset


class IdeaDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Idea.objects.filter(is_archived=False)
    serializer_class = IdeaSerializer


class ArchiveIdeaAPIView(APIView):
    def post(self, request, pk):
        idea = get_object_or_404(Idea, pk=pk)

        idea.is_archived = True
        idea.archived_at = timezone.now()
        idea.save()

        serializer = IdeaSerializer(idea)

        return Response(serializer.data)


# Student APIs
class StudentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


# Meeting APIs
class MeetingListCreateAPIView(generics.ListCreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class MeetingDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
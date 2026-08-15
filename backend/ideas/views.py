from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Idea, Student, Meeting, IdeaChangeLog
from .serializers import (
    IdeaSerializer,
    StudentSerializer,
    MeetingSerializer,
)

# Fields tracked on Idea for the change-log audit trail. Simple scalar
# fields are diffed directly; `students` is handled separately since it's
# a many-to-many relation, not a plain attribute.
IDEA_TRACKED_FIELDS = ["title", "description", "status", "priority"]


def _label_for_students(student_ids):
    names = list(
        Student.objects.filter(id__in=student_ids).values_list("name", flat=True)
    )
    return ", ".join(sorted(names)) if names else "(none)"


def log_idea_changes(idea, old_values, old_student_ids):
    """Write one IdeaChangeLog row per field that actually changed."""
    logs = []

    for field in IDEA_TRACKED_FIELDS:
        new_value = getattr(idea, field)
        if old_values.get(field) != new_value:
            logs.append(IdeaChangeLog(
                idea=idea,
                field=field,
                old_value=old_values.get(field),
                new_value=new_value,
            ))

    if old_student_ids is not None:
        new_student_ids = set(idea.students.values_list("id", flat=True))

        if old_student_ids != new_student_ids:
            logs.append(IdeaChangeLog(
                idea=idea,
                field="students",
                old_value=_label_for_students(old_student_ids),
                new_value=_label_for_students(new_student_ids),
            ))

    if logs:
        IdeaChangeLog.objects.bulk_create(logs)


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

    def perform_update(self, serializer):
        idea = self.get_object()

        old_values = {field: getattr(idea, field) for field in IDEA_TRACKED_FIELDS}

        old_student_ids = (
            set(idea.students.values_list("id", flat=True))
            if "students" in serializer.validated_data
            else None
        )

        updated_idea = serializer.save()

        log_idea_changes(updated_idea, old_values, old_student_ids)


class ArchiveIdeaAPIView(APIView):
    def post(self, request, pk):
        idea = get_object_or_404(Idea, pk=pk)

        idea.is_archived = True
        idea.archived_at = timezone.now()
        idea.save()

        IdeaChangeLog.objects.create(
            idea=idea,
            field="is_archived",
            old_value="False",
            new_value="True",
        )

        serializer = IdeaSerializer(idea)

        return Response(serializer.data)

class UnarchiveIdeaAPIView(APIView):
    def post(self, request, pk):
        idea = get_object_or_404(Idea, pk=pk)

        idea.is_archived = False
        idea.archived_at = None
        idea.save()

        IdeaChangeLog.objects.create(
            idea=idea,
            field="is_archived",
            old_value="True",
            new_value="False",
        )

        serializer = IdeaSerializer(idea)

        return Response(serializer.data)


# Student APIs
class StudentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


# Meeting APIs
class MeetingListCreateAPIView(generics.ListCreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class MeetingDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

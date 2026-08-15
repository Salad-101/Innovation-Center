from rest_framework import serializers

from .models import Student, Idea, Meeting, IdeaChangeLog


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = [
            "id",
            "student_id",
            "name",
            "email",
            "phone",
            "department",
        ]


class MeetingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Meeting
        fields = "__all__"


class IdeaChangeLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = IdeaChangeLog
        fields = [
            "id",
            "idea",
            "field",
            "old_value",
            "new_value",
            "changed_at",
        ]


class IdeaSerializer(serializers.ModelSerializer):

    students = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Student.objects.all()
    )

    meetings = MeetingSerializer(
        many=True,
        read_only=True
    )

    change_logs = IdeaChangeLogSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Idea
        fields = "__all__"
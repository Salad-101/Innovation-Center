from django.contrib import admin

from .models import Student, Idea, Meeting


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "name", "department")
    search_fields = ("student_id", "name", "email")


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "priority", "is_archived", "created_at")
    list_filter = ("status", "priority", "is_archived")
    search_fields = ("title", "description")
    filter_horizontal = ("students",)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("idea", "date", "time", "location")
    list_filter = ("date",)
    search_fields = ("idea__title", "location")
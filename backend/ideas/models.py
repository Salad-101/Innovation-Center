from django.db import models


class Student(models.Model):
    student_id = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class Idea(models.Model):

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        REVIEW = "REVIEW", "Under Review"
        REFINEMENT = "REFINEMENT", "Needs Refinement"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    title = models.CharField(max_length=200)

    description = models.TextField()

    students = models.ManyToManyField(
        Student,
        related_name="ideas",
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    is_archived = models.BooleanField(default=False)

    archived_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Meeting(models.Model):

    idea = models.ForeignKey(
        Idea,
        on_delete=models.CASCADE,
        related_name="meetings"
    )

    date = models.DateField()

    time = models.TimeField()

    location = models.CharField(
        max_length=200,
        blank=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.idea.title} - {self.date}"
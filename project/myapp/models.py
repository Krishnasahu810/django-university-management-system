from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):\n    USER_TYPE_CHOICES = [\n        ('student', 'Student'),\n        ('admin', 'Admin'),\n        ('instructor', 'Instructor'),\n    ]\n\n    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')\n\n    def __str__(self):\n        return self.username


class Course(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Completed', 'Completed'),
    ]

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    instructor = models.ForeignKey('Instructor', null=True, blank=True, on_delete=models.SET_NULL, related_name='courses')
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    status = models.CharField(choices=STATUS_CHOICES, default='Active', max_length=20)
    semester = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Instructor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(blank=True, max_length=15)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Enrollment(models.Model):
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_date = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        ordering = ['-enrolled_date']
        unique_together = (('student', 'course'),)

    def __str__(self):
        return f"{self.student.username} in {self.course.code}"


class Attendance(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance_records')
    classes_held = models.IntegerField(default=0)
    present = models.IntegerField(default=0)
    absent = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        
        pass

    def percentage(self):
        return (self.present / self.classes_held * 100) if self.classes_held > 0 else 0

    def __str__(self):
        return f"Attendance for {self.enrollment.student.username} in {self.enrollment.course.code}"

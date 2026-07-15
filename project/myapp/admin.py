from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Course, Attendance, Instructor, Enrollment


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
	search_fields = ('username', 'email', 'first_name', 'last_name')
	ordering = ('username',)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
	list_display = ('first_name', 'last_name', 'email')
	search_fields = ('first_name', 'last_name', 'email')
	ordering = ('last_name', 'first_name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
	list_display = ('code', 'name', 'instructor', 'credits', 'status')
	search_fields = ('code', 'name')
	ordering = ('code',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
	list_display = ('student', 'course', 'enrolled_date', 'grade')
	list_filter = ('course',)
	ordering = ('-enrolled_date',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ('enrollment', 'classes_held', 'present', 'absent', 'updated_at')
	list_filter = ('enrollment__course',)
	ordering = ('-updated_at',)

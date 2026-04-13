from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Course, Attendance, Instructor, Enrollment, Marks


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ()}),
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'instructor', 'credits', 'status', 'semester')
    search_fields = ('code', 'name')
    list_filter = ('status', 'semester')
    ordering = ('code',)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_date', 'grade')
    search_fields = ('student__username', 'course__code')
    list_filter = ('enrolled_date', 'course')
    readonly_fields = ('enrolled_date',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_student', 'get_course', 'classes_held', 'present', 'absent', 'get_percentage')
    search_fields = ('enrollment__student__username', 'enrollment__course__code')
    list_filter = ('updated_at', 'enrollment__course')
    readonly_fields = ('updated_at',)
    
    def get_student(self, obj):
        return obj.enrollment.student.username
    get_student.short_description = 'Student'
    
    def get_course(self, obj):
        return obj.enrollment.course.code
    get_course.short_description = 'Course'
    
    def get_percentage(self, obj):
        return f"{obj.percentage():.1f}%"
    get_percentage.short_description = 'Attendance %'


@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('get_student', 'get_course', 'assignment', 'midterm', 'final', 'get_total')
    search_fields = ('enrollment__student__username', 'enrollment__course__code')
    list_filter = ('updated_at', 'enrollment__course')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_student(self, obj):
        return obj.enrollment.student.username
    get_student.short_description = 'Student'
    
    def get_course(self, obj):
        return obj.enrollment.course.code
    get_course.short_description = 'Course'
    
    def get_total(self, obj):
        return obj.total()
    get_total.short_description = 'Total Marks'




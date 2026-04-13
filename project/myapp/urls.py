from django.urls import path
from . import views

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Student views
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('courses/', views.courses, name='courses'),
    path('attendance/', views.attendance, name='attendance'),
    path('marks/', views.marks, name='marks'),
    
    # Admin Panel Views (Changed prefix to avoid conflict with Django's /admin/)
    path('staff/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/users/', views.admin_users, name='admin_users'),
    path('staff/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('staff/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    
    path('staff/courses/', views.admin_courses, name='admin_courses'),
    path('staff/courses/create/', views.admin_course_create, name='admin_course_create'),
    path('staff/courses/<int:course_id>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('staff/courses/<int:course_id>/delete/', views.admin_course_delete, name='admin_course_delete'),
    
    path('staff/attendance/', views.admin_attendance, name='admin_attendance'),
    path('staff/attendance/create/', views.admin_attendance_create, name='admin_attendance_create'),
    
    path('staff/marks/', views.admin_marks, name='admin_marks'),
    path('staff/marks/create/', views.admin_marks_create, name='admin_marks_create'),
    
    path('staff/enrollments/', views.admin_enrollments, name='admin_enrollments'),
    path('staff/enrollments/create/', views.admin_enrollment_create, name='admin_enrollment_create'),
]


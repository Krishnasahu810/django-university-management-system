from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('courses/', views.courses, name='courses'),
    path('courses/create/', views.course_create, name='course_create'),
    path('attendance/', views.attendance, name='attendance'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('marks/', views.marks, name='marks'),
]

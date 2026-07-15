from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from functools import wraps
from .forms import SignupForm, LoginForm
from .models import Course, Attendance, Enrollment, CustomUser, Marks, Instructor
from .forms import CourseForm, AttendanceForm, MarksForm


# ========== DECORATORS ==========

def admin_required(view_func):
    """Decorator to restrict view access to admin users only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin():
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """Decorator to restrict view access to student users only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_student():
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


# ========== PUBLIC VIEWS ==========

def home(request):
    """Redirect to appropriate dashboard based on user role"""
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('admin_dashboard')
        else:
            return redirect('dashboard')
    return redirect('login')


def signup_view(request):
    """Allow new students to register"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'  # New users are always students
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    """Login view for both admin and students"""
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('admin_dashboard')
        else:
            return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect admin to admin dashboard, students to student dashboard
            if user.is_admin():
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login')


# ========== STUDENT VIEWS ==========

@login_required(login_url='login')
@student_required
def dashboard(request):
    """Student dashboard - shows only their own data"""
    # Get only user's enrollments
    user_enrollments = request.user.enrollments.all()
    total_courses = user_enrollments.count()

    attendance_total_classes = 0
    attendance_present = 0
    attendance_absent = 0

    for enrollment in user_enrollments:
        att = enrollment.attendance_records.order_by('-updated_at').first()
        if att:
            attendance_total_classes += att.classes_held
            attendance_present += att.present
            attendance_absent += att.absent

    attendance_percentage = (attendance_present / attendance_total_classes * 100) if attendance_total_classes > 0 else 0
    
    # Calculate average marks
    avg_marks = 0
    marks_count = 0
    for enrollment in user_enrollments:
        mark = enrollment.marks_records.first()
        if mark:
            avg_marks += mark.total()
            marks_count += 1
    
    if marks_count > 0:
        avg_marks = avg_marks / marks_count

    context = {
        'total_courses': total_courses,
        'attendance': round(attendance_percentage, 1),
        'average_marks': round(avg_marks, 1),
        'enrollments_count': total_courses,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
@student_required
def student_profile(request):
    """Student can view their own profile"""
    user = request.user
    context = {'user': user}
    return render(request, 'student_profile.html', context)


@login_required(login_url='login')
@student_required
def courses(request):
    """Students see only their enrolled courses"""
    # Show only user's enrolled courses
    user_courses = request.user.enrollments.all().values_list('course', flat=True)
    courses = Course.objects.filter(id__in=user_courses)
    
    courses_data = []
    for c in courses:
        instructor_name = str(c.instructor) if getattr(c, 'instructor', None) else 'N/A'
        courses_data.append({
            'code': c.code,
            'name': c.name,
            'credits': c.credits,
            'instructor': instructor_name,
            'status': c.status,
        })
    context = {'courses': courses_data}
    return render(request, 'courses.html', context)


@login_required(login_url='login')
@student_required
def attendance(request):
    """Students see their own attendance"""
    course_attendance = []
    total_classes = 0
    present_count = 0
    absent_count = 0

    # Only user's enrollments
    for enrollment in request.user.enrollments.all():
        att = enrollment.attendance_records.order_by('-updated_at').first()
        if att:
            total_classes += att.classes_held
            present_count += att.present
            absent_count += att.absent
            
            percentage = (att.present / att.classes_held * 100) if att.classes_held > 0 else 0
            
            course_attendance.append({
                'code': enrollment.course.code,
                'name': enrollment.course.name,
                'classes_held': att.classes_held,
                'present': att.present,
                'absent': att.absent,
                'percentage': round(percentage, 1),
            })

    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

    context = {
        'course_attendance': course_attendance,
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': round(attendance_percentage, 1),
    }
    return render(request, 'attendance.html', context)


@login_required(login_url='login')
@student_required
def marks(request):
    """Students see their own marks"""
    user_enrollments = request.user.enrollments.all()
    marks_data = []
    
    for enrollment in user_enrollments:
        mark = enrollment.marks_records.first()
        if mark:
            marks_data.append({
                'course': enrollment.course.code,
                'course_name': enrollment.course.name,
                'assignment': mark.assignment,
                'midterm': mark.midterm,
                'final': mark.final,
                'total': mark.total(),
                'percentage': round(mark.percentage(), 1),
            })
    
    context = {'marks_data': marks_data}
    return render(request, 'marks.html', context)


# ========== ADMIN VIEWS ==========

@login_required(login_url='login')
@admin_required
def admin_dashboard(request):
    """Admin dashboard - overview of all system data"""
    total_students = CustomUser.objects.filter(role='student').count()
    total_admins = CustomUser.objects.filter(role='admin').count()
    total_courses = Course.objects.count()
    total_instructors = Instructor.objects.count()
    total_enrollments = Enrollment.objects.count()
    
    context = {
        'total_students': total_students,
        'total_admins': total_admins,
        'total_courses': total_courses,
        'total_instructors': total_instructors,
        'total_enrollments': total_enrollments,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required(login_url='login')
@admin_required
def admin_users(request):
    """Admin - manage all users"""
    users = CustomUser.objects.all().order_by('role', 'first_name')
    context = {'users': users}
    return render(request, 'admin_users.html', context)


@login_required(login_url='login')
@admin_required
def admin_user_edit(request, user_id):
    """Admin - edit user details"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.role = request.POST.get('role', user.role)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()
        return redirect('admin_users')
    
    context = {'user': user}
    return render(request, 'admin_user_edit.html', context)


@login_required(login_url='login')
@admin_required
def admin_user_delete(request, user_id):
    """Admin - delete user"""
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('admin_users')
    context = {'user': user}
    return render(request, 'admin_user_delete.html', context)


@login_required(login_url='login')
@admin_required
def admin_courses(request):
    """Admin - manage all courses"""
    courses = Course.objects.all()
    context = {'courses': courses}
    return render(request, 'admin_courses.html', context)


@login_required(login_url='login')
@admin_required
def admin_course_create(request):
    """Admin - create new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_courses')
    else:
        form = CourseForm()
    return render(request, 'admin_course_form.html', {'form': form})


@login_required(login_url='login')
@admin_required
def admin_course_edit(request, course_id):
    """Admin - edit course"""
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('admin_courses')
    else:
        form = CourseForm(instance=course)
    return render(request, 'admin_course_form.html', {'form': form})


@login_required(login_url='login')
@admin_required
def admin_course_delete(request, course_id):
    """Admin - delete course"""
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('admin_courses')
    context = {'course': course}
    return render(request, 'admin_course_delete.html', context)


@login_required(login_url='login')
@admin_required
def admin_attendance(request):
    """Admin - view all attendance records"""
    attendance_records = Attendance.objects.all().select_related('enrollment__student', 'enrollment__course')
    context = {'attendance_records': attendance_records}
    return render(request, 'admin_attendance.html', context)


@login_required(login_url='login')
@admin_required
def admin_attendance_create(request):
    """Admin - create/update attendance record"""
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            course = form.cleaned_data['course']
            classes_held = form.cleaned_data['classes_held']
            present = form.cleaned_data['present']
            absent = form.cleaned_data['absent']

            enrollment, _ = Enrollment.objects.get_or_create(student=student, course=course)
            Attendance.objects.update_or_create(
                enrollment=enrollment,
                defaults={
                    'classes_held': classes_held,
                    'present': present,
                    'absent': absent,
                }
            )
            return redirect('admin_attendance')
    else:
        form = AttendanceForm()
    return render(request, 'admin_attendance_form.html', {'form': form})


@login_required(login_url='login')
@admin_required
def admin_marks(request):
    """Admin - view all marks"""
    marks_records = Marks.objects.all().select_related('enrollment__student', 'enrollment__course')
    context = {'marks_records': marks_records}
    return render(request, 'admin_marks.html', context)


@login_required(login_url='login')
@admin_required
def admin_marks_create(request):
    """Admin - create/update marks"""
    if request.method == 'POST':
        student_id = request.POST.get('student')
        course_id = request.POST.get('course')
        
        student = get_object_or_404(CustomUser, id=student_id, role='student')
        course = get_object_or_404(Course, id=course_id)
        
        enrollment, _ = Enrollment.objects.get_or_create(student=student, course=course)
        
        marks_obj, created = Marks.objects.get_or_create(enrollment=enrollment)
        marks_obj.assignment = int(request.POST.get('assignment', 0))
        marks_obj.midterm = int(request.POST.get('midterm', 0))
        marks_obj.final = int(request.POST.get('final', 0))
        marks_obj.save()
        
        return redirect('admin_marks')
    
    students = CustomUser.objects.filter(role='student')
    courses = Course.objects.all()
    context = {'students': students, 'courses': courses}
    return render(request, 'admin_marks_form.html', context)


@login_required(login_url='login')
@admin_required
def admin_enrollments(request):
    """Admin - manage student enrollments"""
    enrollments = Enrollment.objects.all().select_related('student', 'course')
    context = {'enrollments': enrollments}
    return render(request, 'admin_enrollments.html', context)


@login_required(login_url='login')
@admin_required
def admin_enrollment_create(request):
    """Admin - create enrollment"""
    if request.method == 'POST':
        student_id = request.POST.get('student')
        course_id = request.POST.get('course')
        
        student = get_object_or_404(CustomUser, id=student_id)
        course = get_object_or_404(Course, id=course_id)
        
        enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
        return redirect('admin_enrollments')
    
    students = CustomUser.objects.filter(role='student')
    courses = Course.objects.all()
    context = {'students': students, 'courses': courses}
    return render(request, 'admin_enrollment_form.html', context)

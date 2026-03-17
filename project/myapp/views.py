from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from .forms import SignupForm, LoginForm
from .models import Course, Attendance, Enrollment, CustomUser
from .forms import CourseForm, AttendanceForm


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.user_type = 'student'
            user.save()
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def admin_dashboard(request):
    users = CustomUser.objects.all().order_by('-is_staff', 'username')
    courses_count = Course.objects.count()
    enrollments_count = Enrollment.objects.count()
    context = {
        'users': users,
        'courses_count': courses_count,
        'enrollments_count': enrollments_count,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff)
def student_dashboard(request):
    # Personal dashboard for students only
    user_enrollments = Enrollment.objects.filter(student=request.user)
    total_courses = user_enrollments.count()
    
    attendance_total_classes = 0
    attendance_present = 0
    
    for enrollment in user_enrollments:
        att = enrollment.attendance_records.order_by('-updated_at').first()
        if att:
            attendance_total_classes += att.classes_held
            attendance_present += att.present
    
    attendance_percentage = (attendance_present / attendance_total_classes * 100) if attendance_total_classes > 0 else 0

    context = {
        'total_courses': total_courses,
        'attendance': round(attendance_percentage, 1),
        'average_marks': 78,
        'current_year': 3,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def student_profile(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    user = request.user
    context = {'user': user}
    return render(request, 'student_profile.html', context)


@login_required(login_url='login')
def courses(request):
    if request.user.is_staff:
        courses = Course.objects.all()
    else:
        enrollments = Enrollment.objects.filter(student=request.user)
        courses = [e.course for e in enrollments]
    courses_data = []
    for c in courses:
        instructor_name = str(c.instructor) if getattr(c, 'instructor', None) else ''
        courses_data.append({
            'code': c.code,
            'name': c.name,
            'credits': c.credits,
            'instructor': instructor_name,
            'status': c.status,
        })
    context = {'courses': courses_data}
    return render(request, 'courses.html', context)


@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='login')
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('courses')
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form})


@login_required(login_url='login')
def attendance(request):
    if request.user.is_staff:
        course_attendance = []
        total_classes = 0
        present_count = 0
        absent_count = 0

        for course in Course.objects.all():
            classes_held = 0
            present = 0
            absent = 0
            for enrollment in course.enrollments.all():
                att = enrollment.attendance_records.order_by('-updated_at').first()
                if att:
                    classes_held += att.classes_held
                    present += att.present
                    absent += att.absent

            percentage = (present / classes_held * 100) if classes_held > 0 else 0
            percentage = round(percentage, 1)

            course_attendance.append({
                'code': course.code,
                'name': course.name,
                'classes_held': classes_held,
                'present': present,
                'absent': absent,
                'percentage': percentage,
            })

            total_classes += classes_held
            present_count += present
            absent_count += absent

        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
    else:
        user_enrollments = Enrollment.objects.filter(student=request.user)
        course_attendance = []
        for enrollment in user_enrollments:
            course = enrollment.course
            att = enrollment.attendance_records.order_by('-updated_at').first()
            if att:
                percentage = att.percentage()
                course_attendance.append({
                    'code': course.code,
                    'name': course.name,
                    'classes_held': att.classes_held,
                    'present': att.present,
                    'absent': att.absent,
                    'percentage': round(percentage, 1),
                })

        total_classes = sum(att.classes_held for att in [e.attendance_records.order_by('-updated_at').first() for e in user_enrollments if e.attendance_records.order_by('-updated_at').first()])
        attendance_percentage = 0  # Simplified

    context = {
        'course_attendance': course_attendance,
        'total_classes': total_classes,
        'attendance_percentage': round(attendance_percentage, 1),
    }
    return render(request, 'attendance.html', context)


@user_passes_test(lambda u: u.is_staff)
@login_required(login_url='login')
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            course = form.cleaned_data['course']
            classes_held = form.cleaned_data['classes_held']
            present = form.cleaned_data['present']
            absent = form.cleaned_data['absent']

            enrollment, _ = Enrollment.objects.get_or_create(student=student, course=course)
            Attendance.objects.create(
                enrollment=enrollment,
                classes_held=classes_held,
                present=present,
                absent=absent,
            )
            return redirect('attendance')
    else:
        form = AttendanceForm()
    return render(request, 'attendance_form.html', {'form': form})


def marks(request):
    if request.user.is_authenticated and not request.user.is_staff:
        # Student marks
        pass
    context = {
        'marks_data': [
            {'course': 'CS101', 'marks': 85},
            {'course': 'MATH201', 'marks': 78},
            {'course': 'PHY301', 'marks': 92},
        ]
    }
    return render(request, 'marks.html', context)

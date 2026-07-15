from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm
from .models import Course, Attendance, Enrollment
from .forms import CourseForm, AttendanceForm

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    courses = Course.objects.all()

    attendance_total_classes = 0
    attendance_present = 0
    attendance_absent = 0

    for course in courses:
        for enrollment in course.enrollments.all():
            att = enrollment.attendance_records.order_by('-updated_at').first()
            if att:
                attendance_total_classes += att.classes_held
                attendance_present += att.present
                attendance_absent += att.absent

    attendance_percentage = (attendance_present / attendance_total_classes * 100) if attendance_total_classes > 0 else 0

    context = {
        'total_courses': courses.count(),
        'attendance': round(attendance_percentage, 1),
        'average_marks': 78,
        'current_year': 3,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def student_profile(request):
    user = request.user
    context = {'user': user}
    return render(request, 'student_profile.html', context)


@login_required(login_url='login')
def courses(request):
    courses = Course.objects.all()
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

    context = {
        'course_attendance': course_attendance,
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': round(attendance_percentage, 1),
    }
    return render(request, 'attendance.html', context)


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
    context = {
        'marks_data': [
            {'course': 'CS101', 'marks': 85},
            {'course': 'MATH201', 'marks': 78},
            {'course': 'PHY301', 'marks': 92},
        ]
    }
    return render(request, 'marks.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserForm, StudentForm, MentorForm, LeaveForm
from .models import Student, Mentor, Leave
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
def home(request):
    return render(request, 'home.html')

def signup_student(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            student = student_form.save(commit=False)
            student.user = user
            student.save()
            students_group, created = Group.objects.get_or_create(name='Studentss')
            user.groups.add(students_group)
            mentors = Mentor.objects.all()
            for mentor in mentors:
                send_mail(
                    'New Student Signup',
                    f'Approve or reject the new {student.name}: http://localhost:8000/approve_student/{student.id}/ or http://localhost:8000/reject_student/{student.id}/',
                    settings.EMAIL_HOST_USER,
                    [mentor.user.email],
                    fail_silently=False
                )
            return render(request, 'success.html', {'message': 'Sign up successful. Awaiting approval.'})
    else:
        user_form = UserForm()
        student_form = StudentForm()
    return render(request, 'signup_student.html', {'user_form': user_form, 'student_form': student_form})

def signup_mentor(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        mentor_form = MentorForm(request.POST)
        if user_form.is_valid() and mentor_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            mentor_group, created = Group.objects.get_or_create(name='Mentor')
            user.groups.add(mentor_group)
            mentor = mentor_form.save(commit=False)
            mentor.user = user
            mentor.save()
            login(request, user)
            return redirect('mentor_dashboard')
    else:
        user_form = UserForm()
        mentor_form = MentorForm()
    return render(request, 'signup_mentor.html', {'user_form': user_form, 'mentor_form': mentor_form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    if request.user.groups.filter(name='Mentor').exists():
        return redirect('mentor_dashboard')
    elif request.user.groups.filter(name='Students').exists():
        # Check employee approval status before redirecting
        student = Student.objects.get(user=request.user)
        if not student.is_approved:
            return render(request, 'error.html', {'message': 'Your account is not approved yet.'})
        return redirect('student_dashboard')
    else:
        return render(request, 'error.html', {'message': 'You do not have the required permissions to access any dashboard.'})

@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return render(request, 'error.html', {'message': 'No Student matches the given query.'})

    if not student.is_approved:
        return render(request, 'error.html', {'message': 'Your account is not approved yet.'})

    leave_requests = Leave.objects.filter(student=student)
    return render(request, 'student_dashboard.html', {'leave_requests': leave_requests})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Mentor').exists())
def mentor_dashboard(request):
    try:
        manager = Mentor.objects.get(user=request.user)
    except Mentor.DoesNotExist:
        return render(request, 'error.html', {'message': 'No Manager matches the given query.'})

    students = Student.objects.filter(manager=manager)
    return render(request, 'mentor_dashboard.html', {'students': students})
@login_required
def apply_leave(request):
    if request.method == 'POST':
        leave_form = LeaveForm(request.POST)
        if leave_form.is_valid():
            leave = leave_form.save(commit=False)
            leave.student = get_object_or_404(Student, user=request.user)
            leave.status = 'Pending'
            leave.save()
            return redirect('student_dashboard')
    else:
        leave_form = LeaveForm()
    return render(request, 'apply_leave.html', {'leave_form': leave_form})
@login_required
def show_leave_requests(request):
    mentor = get_object_or_404(Mentor, user=request.user)
    students = Student.objects.filter(manager=mentor)
    leave_requests = Leave.objects.filter(student__in=students)
    return render(request, 'show_leave_requests.html', {'leave_requests': leave_requests})
@login_required
def manage_leave_request(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)
    if request.method == 'POST':
        leave.status = request.POST['status']
        leave.save()
        send_mail(
            'Leave Request Update',
            f'Your leave request has been {leave.status.lower()}.',
            settings.EMAIL_HOST_USER,
            [leave.employee.user.email],
            fail_silently=False
        )
        return redirect('show_leave_requests')
    return render(request, 'mentor_leave_request.html', {'leave': leave})
@login_required
def approve_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.is_approved = True
    student.save()
    send_mail(
        'Student Approved',
        'Your sign-up request has been approved.',
        settings.EMAIL_HOST_USER,
        [student.user.email],
        fail_silently=False
    )
    return redirect('mentorr_dashboard')
@login_required
def reject_student(request, employee_id):
    student= get_object_or_404(Student, id=employee_id)
    student.user.delete()
    student.delete()
    send_mail(
        'Student Rejected',
        'Your sign-up request has been rejected.',
        settings.EMAIL_HOST_USER,
        [student.user.email],
        fail_silently=False
    )
    return redirect('mentor_dashboard')

# forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Student, Mentor, Leave

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

class MentorForm(forms.ModelForm):
    class Meta:
        model = Mentor
        fields = ['name', 'mentor_id', 'department']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'student_id', 'department', 'year', 'mentor']

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['start_date', 'end_date', 'reason']

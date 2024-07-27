from django.contrib import admin
from django.urls import path
from employees import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/student/', views.signup_student, name='signup_student'),
    path('signup/mentor/', views.signup_mentor, name='signup_mentor'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('mentor_dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('apply_leave/', views.apply_leave, name='apply_leave'),
    path('show_leave_requests/', views.show_leave_requests, name='show_leave_requests'),
    path('manage_leave_request/<int:leave_id>/', views.manage_leave_request, name='manage_leave_request'),
    path('approve_employee/<int:employee_id>/', views.approve_student, name='approve_student'),
    path('reject_employee/<int:employee_id>/', views.reject_student, name='reject_student'),
]

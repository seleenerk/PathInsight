from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'users'

urlpatterns = [
    path('register/jobseeker/', views.register_jobseeker, name='register_jobseeker'),
    path('register/employer/', views.register_employer, name='register_employer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/jobseeker/', views.jobseeker_dashboard, name='jobseeker_dashboard'),
    path('dashboard/employer/', views.employer_dashboard, name='employer_dashboard'),
    path('survey/', views.survey_view, name='survey'),
    path('jobseeker/delete-cv/', views.delete_cv_view, name='delete_cv'),
    path('employer/create-job/', views.create_job_posting, name='create_job_posting'),
    path('employer/edit-job/<int:pk>/', views.edit_job_posting, name='edit_job_posting'),
    path('employer/delete-job/<int:pk>/', views.delete_job_posting, name='delete_job_posting'),
    path('job-listings/', views.job_listings_view, name='job_listings'),
    path('apply/<int:job_id>/', views.apply_job_view, name='apply_job'),
    path('update-employer-profile/', views.update_employer_profile, name='update_employer_profile'),
    path('jobseeker/update-profile/', views.update_jobseeker_profile, name='update_jobseeker_profile'),
    path('start-matching/', views.start_matching, name='start_matching'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/delete/jobseeker/<int:pk>/', views.delete_jobseeker, name='delete_jobseeker'),
    path('admin/delete/employer/<int:pk>/', views.delete_employer, name='delete_employer'),
    path('admin/delete/job/<int:pk>/', views.delete_job_posting, name='delete_job_posting'),
    path('applicant/<int:jobseeker_id>/profile/', views.view_applicant_profile, name='view_applicant_profile'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexPage, name='index'),
    path('login/', views.LoginPage, name='login'),
    path('signup/', views.signup, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('logout/', views.LogoutPage, name='logout'),

    # Candidate / Company Profile
    path('candidate/create/', views.CreateCandidate, name='create_candidate'),
    path('company/create/', views.CreateCompany, name='create_company'),
    path('profile/', views.ViewProfile, name='profile'),
    path('candidate/update/', views.UpdateCandidate, name='update_candidate'),
    path('company/update/', views.UpdateCompany, name='update_company'),

    # Admin Panel
    path('myadmin/dashboard/', views.AdminDashboard, name='admin_dashboard'),
    path('myadmin/companies/', views.AdminViewCompanies, name='admin_companies'),
    path('myadmin/candidates/', views.AdminViewCandidates, name='admin_candidates'),
    path('myadmin/delete/<int:id>/', views.AdminDeleteUser, name='admin_delete'),

    # Company Job Posting
    path('company/post-job/', views.CompanyPostJob, name='company_post_job'),
    path('company/my-jobs/', views.CompanyMyJobs, name='company_my_jobs'),
    path('company/delete-job/<int:id>/', views.CompanyDeleteJob, name='company_delete_job'),
    path('company/job/<int:id>/applicants/', views.CompanyJobApplicants, name='company_applicants'),
    
    # Job Detail + Apply
    path('job/<int:id>/', views.JobDetailPage, name='job_detail'),
    path('job/apply/<int:id>/', views.ApplyJob, name='apply_job'),
    path('candidate/my-applications/', views.CandidateApplications, name='my_applications'),
]
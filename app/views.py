from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from .models import Master, Candidate, Company, Job, Application

def IndexPage(request):
    from .models import Job, Company, Candidate
    # search if user typed
    q = request.GET.get('q')
    if q:
        jobs = Job.objects.filter(title__icontains=q).order_by('-created_at')
    else:
        jobs = Job.objects.all().order_by('-created_at')[:10]
    
    context = {
        'jobs': jobs,
        'job_count': Job.objects.count(),
        'company_count': Company.objects.count(),
        'candidate_count': Candidate.objects.count(),
    }
    return render(request, "app/index.html", context)

def send_otp_email(email, otp):
    subject = 'JobBoard - OTP Verification'
    message = f'Hello,\n\nYour OTP for JobBoard registration is: {otp}\nValid for 5 minutes.\n\nDo not share it.'
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        role = request.POST.get('role')

        if password!= repassword:
            messages.error(request, "Passwords do not match")
            return redirect('login')

        if Master.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('login')

        master = Master.objects.create(
            email=email,
            password=make_password(password),
            role=role,
            is_active=False,
            is_verified=False
        )
        master.generate_otp()
        send_otp_email(email, master.otp)
        request.session['verify_email'] = email
        messages.success(request, f"OTP sent to {email}")
        return redirect('login')
    return redirect('login')

def verify_otp(request):
    email = request.session.get('verify_email')
    if not email:
        return redirect('login')
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        try:
            master = Master.objects.get(email=email)
            success, msg = master.verify_otp(entered_otp)
            if success:
                del request.session['verify_email']
                messages.success(request, "Email verified! Please login now.")
                return redirect('login')
            else:
                if msg == 'expired':
                    messages.error(request, "OTP expired. New OTP sent.")
                    master.generate_otp()
                    send_otp_email(email, master.otp)
                else:
                    messages.error(request, "Invalid OTP")
        except Master.DoesNotExist:
            messages.error(request, "User not found")
    return redirect('login')

def resend_otp(request):
    email = request.session.get('verify_email')
    if email:
        try:
            master = Master.objects.get(email=email)
            master.generate_otp()
            send_otp_email(email, master.otp)
            messages.success(request, "New OTP sent")
        except:
            messages.error(request, "Error resending OTP")
    return redirect('login')

def LoginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            master = Master.objects.get(email=email)
            if not master.is_verified:
                request.session['verify_email'] = email
                master.generate_otp()
                send_otp_email(email, master.otp)
                messages.error(request, "Please verify email first. New OTP sent.")
                return redirect('login')
            if check_password(password, master.password):
                request.session['master_id'] = master.id
                request.session['email'] = master.email
                request.session['role'] = master.role

                # --- ADMIN CHECK ADDED HERE ---
                if master.role == 'admin':
                    messages.success(request, "Admin Login Successful!")
                    return redirect('admin_dashboard')

                if master.role == 'candidate':
                    if not Candidate.objects.filter(master=master).exists():
                        return redirect('create_candidate')
                elif master.role == 'company':
                    if not Company.objects.filter(master=master).exists():
                        return redirect('create_company')

                messages.success(request, "Login successful!")
                if master.role == 'company':
                    return redirect('company_my_jobs')
                elif master.role == 'candidate':
                    return redirect('index')
                else:
                    return redirect('index')
            else:
                messages.error(request, "Invalid password")
        except Master.DoesNotExist:
            messages.error(request, "Email not registered")
    return render(request, "app/login.html")

def LogoutPage(request):
    request.session.flush()
    return redirect('login')

def CreateCandidate(request):
    master_id = request.session.get('master_id')
    if not master_id:
        return redirect('login')
    master = Master.objects.get(id=master_id)

    if Candidate.objects.filter(master=master).exists():
        return redirect('index')

    if request.method == 'POST':
        Candidate.objects.create(
            master=master,
            firstname=request.POST.get('firstname'),
            lastname=request.POST.get('lastname'),
            contact=request.POST.get('contact'),
            state=request.POST.get('state'),
            city=request.POST.get('city'),
            address=request.POST.get('address'),
            dob=request.POST.get('dob'),
            gender=request.POST.get('gender'),
            profile_pic=request.FILES.get('profile_pic')
        )
        messages.success(request, "Profile Created!")
        return redirect('index')
    return render(request, "app/candidate_profile.html")

def CreateCompany(request):
    master_id = request.session.get('master_id')
    if not master_id:
        return redirect('login')
    master = Master.objects.get(id=master_id)

    if Company.objects.filter(master=master).exists():
        return redirect('index')

    if request.method == 'POST':
        Company.objects.create(
            master=master,
            firstname=request.POST.get('firstname'),
            lastname=request.POST.get('lastname'),
            company_name=request.POST.get('company_name'),
            state=request.POST.get('state'),
            city=request.POST.get('city'),
            contact=request.POST.get('contact'),
            address=request.POST.get('address'),
            logo_pic=request.FILES.get('logo_pic')
        )
        messages.success(request, "Company Profile Created!")
        return redirect('company_my_jobs')
    return render(request, "app/company_profile.html")

def ViewProfile(request):
    master_id = request.session.get('master_id')
    if not master_id:
        return redirect('login')
    master = Master.objects.get(id=master_id)
    context = {}
    if master.role == 'candidate':
        context['profile'] = Candidate.objects.get(master=master)
    else:
        context['profile'] = Company.objects.get(master=master)
    context['master'] = master
    return render(request, "app/profile.html", context)

def UpdateCandidate(request):
    master_id = request.session.get('master_id')
    if not master_id:
        return redirect('login')
    master = Master.objects.get(id=master_id)
    candidate = Candidate.objects.get(master=master)

    if request.method == 'POST':
        candidate.firstname = request.POST.get('firstname')
        candidate.lastname = request.POST.get('lastname')
        candidate.contact = request.POST.get('contact')
        candidate.city = request.POST.get('city')
        candidate.state = request.POST.get('state')
        candidate.address = request.POST.get('address')
        if request.POST.get('gender'):
            candidate.gender = request.POST.get('gender')
        if request.POST.get('dob'):
            candidate.dob = request.POST.get('dob')
        if request.FILES.get('profile_pic'):
            candidate.profile_pic = request.FILES.get('profile_pic')
        candidate.save()
        messages.success(request, "Profile Updated!")
        return redirect('profile')
    return render(request, "app/update_candidate.html", {'profile': candidate})

def UpdateCompany(request):
    master_id = request.session.get('master_id')
    if not master_id:
        return redirect('login')
    master = Master.objects.get(id=master_id)
    company = Company.objects.get(master=master)

    if request.method == 'POST':
        company.firstname = request.POST.get('firstname')
        company.lastname = request.POST.get('lastname')
        company.company_name = request.POST.get('company_name')
        company.contact = request.POST.get('contact')
        company.city = request.POST.get('city')
        company.state = request.POST.get('state')
        company.address = request.POST.get('address')
        if request.FILES.get('logo_pic'):
            company.logo_pic = request.FILES.get('logo_pic')
        company.save()
        messages.success(request, "Company Profile Updated!")
        return redirect('profile')
    return render(request, "app/update_company.html", {'profile': company})

# ================= ADMIN PANEL VIEWS =================
def AdminDashboard(request):
    if request.session.get('role')!= 'admin':
        return redirect('login')

    company_count = Company.objects.count()
    candidate_count = Candidate.objects.count()
    master_count = Master.objects.count()

    context = {
        'company_count': company_count,
        'candidate_count': candidate_count,
        'master_count': master_count,
    }
    return render(request, "app/admin/dashboard.html", context)

def AdminViewCompanies(request):
    if request.session.get('role')!= 'admin':
        return redirect('login')
    companies = Company.objects.all()
    return render(request, "app/admin/company_list.html", {'companies': companies})

def AdminViewCandidates(request):
    if request.session.get('role')!= 'admin':
        return redirect('login')
    candidates = Candidate.objects.all()
    return render(request, "app/admin/candidate_list.html", {'candidates': candidates})

def AdminDeleteUser(request, id):
    if request.session.get('role')!= 'admin':
        return redirect('login')
    Master.objects.get(id=id).delete()
    messages.success(request, "User Deleted")
    return redirect('admin_dashboard')

# ===== COMPANY JOB POSTING VIEWS =====
def CompanyPostJob(request):
    if 'email' not in request.session:
        return redirect('login')
    master = Master.objects.get(email=request.session['email'])
    if master.role != 'company':
        return redirect('login')
    company = Company.objects.get(master=master)

    if request.method == 'POST':
        Job.objects.create(
            company=company,
            title=request.POST['title'],
            description=request.POST['description'],
            location=request.POST['location'],
            salary=request.POST['salary'],
            job_type=request.POST['job_type'],
            experience=request.POST['experience'],
            skills=request.POST['skills'],
            vacancy=int(request.POST['vacancy']),
        )
        messages.success(request, "Company Profile Created!")
        return redirect('company_my_jobs')

    return render(request, 'app/company/job_post.html', {'company': company})

def CompanyMyJobs(request):
    if 'email' not in request.session:
        return redirect('login')
    master = Master.objects.get(email=request.session['email'])
    company = Company.objects.get(master=master)
    jobs = Job.objects.filter(company=company).order_by('-created_at')
    return render(request, 'app/company/my_jobs.html', {'jobs': jobs, 'company': company})

def CompanyDeleteJob(request, id):
    if 'email' not in request.session:
        return redirect('login')
    job = Job.objects.get(id=id)
    job.delete()
    messages.success(request, "Job Deleted!")
    return redirect('company_my_jobs')

# ========== JOB DETAIL & APPLY ==========

def JobDetailPage(request, id):
    from .models import Job
    try:
        job = Job.objects.get(id=id)
    except Job.DoesNotExist:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, "Job not found")
        return redirect('index')
    return render(request, "app/job_single.html", {'job': job})

def ApplyJob(request, id):
    from .models import Job, Application, Candidate
    from django.contrib import messages
    from django.shortcuts import redirect, get_object_or_404

    if 'master_id' not in request.session:
        messages.error(request, "Please login to apply")
        return redirect('login')
    
    if request.session.get('role') != 'candidate':
        messages.error(request, "Only candidates can apply. Please login as candidate")
        return redirect('login')

    job = get_object_or_404(Job, id=id)
    
    # Get candidate from master_id (your login system)
    try:
        candidate = Candidate.objects.get(master_id=request.session['master_id'])
    except Candidate.DoesNotExist:
        messages.error(request, "Candidate profile not found. Please create profile first")
        return redirect('create_candidate')

    # Check already applied
    if Application.objects.filter(job=job, candidate=candidate).exists():
        messages.warning(request, "You already applied for this job")
        return redirect('job_detail', id=id)
    
    Application.objects.create(job=job, candidate=candidate)
    messages.success(request, "Applied successfully!")
    return redirect('my_applications')

def CandidateApplications(request):
    from .models import Application, Candidate
    from django.shortcuts import redirect
    
    if 'master_id' not in request.session or request.session.get('role') != 'candidate':
        return redirect('login')
    
    try:
        candidate = Candidate.objects.get(master_id=request.session['master_id'])
    except Candidate.DoesNotExist:
        return redirect('create_candidate')
        
    apps = Application.objects.filter(candidate=candidate).order_by('-applied_at')
    return render(request, "app/my_applications.html", {'applications': apps})

def CompanyJobApplicants(request, id):
    from .models import Job, Application
    from django.shortcuts import redirect, get_object_or_404
    
    if 'master_id' not in request.session or request.session.get('role') != 'company':
        return redirect('login')
    
    job = get_object_or_404(Job, id=id)
    applicants = Application.objects.filter(job=job).order_by('-applied_at')
    return render(request, "app/company_applicants.html", {'job': job, 'applicants': applicants})
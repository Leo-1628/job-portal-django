from django.db import models
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import timedelta

class Master(models.Model):
    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('company', 'Company'),
    )

    email = models.EmailField(max_length=50, unique=True) # unique added
    password = models.CharField(max_length=255) # 50 is too small for hashed passwords
    otp = models.CharField(max_length=6, null=True, blank=True) # changed to CharField, nullable
    otp_created_at = models.DateTimeField(null=True, blank=True) # NEW: for expiry
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=False) # NEW: False until OTP verified
    is_verified = models.BooleanField(default=False)
    is_created = models.DateTimeField(auto_now_add=True)
    is_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    # --- NEW METHODS FOR OTP ---
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp

    def is_otp_expired(self):
        if not self.otp_created_at:
            return True
        return timezone.now() > self.otp_created_at + timedelta(minutes=5)

    def verify_otp(self, otp_entered):
        if self.is_otp_expired():
            return False, "expired"
        if self.otp == otp_entered:
            self.is_verified = True
            self.is_active = True
            self.otp = None # clear OTP after use
            self.save()
            return True, "verified"
        return False, "invalid"

class Candidate(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=150)
    dob = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    profile_pic = models.ImageField(upload_to="app/img/candidate")

    def __str__(self):
        return self.firstname

class Company(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    address = models.CharField(max_length=150)
    logo_pic = models.ImageField(upload_to="app/img/company")

    def __str__(self):
        return self.company_name
    
# ===== JOB POSTING MODELS =====
class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.CharField(max_length=100) # e.g. 5 LPA / 30000 per month
    job_type = models.CharField(max_length=50, choices=[('Full Time','Full Time'),('Part Time','Part Time'),('Internship','Internship'),('Contract','Contract')])
    experience = models.CharField(max_length=100) # e.g. 0-1 years
    skills = models.CharField(max_length=300) # e.g. Python, Django
    vacancy = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Applied', choices=[('Applied','Applied'),('Shortlisted','Shortlisted'),('Rejected','Rejected')])

    class Meta:
        unique_together = ('candidate','job') # One candidate can't apply twice

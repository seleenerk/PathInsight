# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = [
        ('jobseeker', 'Job Seeker'),
        ('employer', 'Employer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    skills = models.CharField(max_length=500, blank=True, null=True)
    education = models.TextField(blank=True)
    work_experience = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    cv_file_path = models.FileField(upload_to='cvs/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class EmployerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    company_name = models.CharField(max_length=255)
    company_description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    industry = models.CharField(max_length=100, blank=True, null=True)
    company_size = models.CharField(
        max_length=50,
        choices=[
            ('1-10', '1–10 employees'),
            ('11-50', '11–50 employees'),
            ('51-200', '51–200 employees'),
            ('200+', '200+ employees')
        ],
        blank=True,
        null=True
    )
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.company_name

class JobListing(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class JobPosting(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    required_skills = models.CharField(max_length=300, help_text="Virgülle ayrılmış şekilde yazınız. Örnek: Python, SQL, Django")
    preferred_traits = models.TextField(
    blank=True,
    help_text="Describe the personal traits or soft skills you're looking for (e.g. teamwork, creativity, attention to detail)."
    )
    company_name = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    founded_year = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return f"{self.title} - {self.employer.user.username}"
        except:
            return self.title

class JobApplication(models.Model):
    jobseeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="applications") 
    application_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.jobseeker.full_name} → {self.job.title}"     
           
class MatchResult(models.Model):
    jobseeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    match_score = models.DecimalField(max_digits=5, decimal_places=2)
    explanation = models.TextField(blank=True, null=True)
    matched_at = models.DateTimeField(auto_now_add=True)
    matched_skills = models.TextField(blank=True, null=True)
    matched_traits = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.jobseeker.full_name} - {self.job.title} ({self.match_score}%)"


class CVAnalysis(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    skills = models.TextField(blank=True)
    education = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    languages = models.TextField(blank=True)
    work_experience = models.TextField(blank=True)
    experience_level = models.CharField(max_length=100, blank=True)
    predicted_role = models.CharField(max_length=100, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user.username} CV Analysis"


class SurveyResponse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    q1_teamwork = models.IntegerField(null=True, blank=True)
    q2_challenging_tasks = models.IntegerField(null=True, blank=True)
    q3_leadership = models.IntegerField(null=True, blank=True)
    q4_uncertainty = models.IntegerField(null=True, blank=True)
    q5_stability = models.IntegerField(null=True, blank=True)

    q6_technology_interest = models.IntegerField(null=True, blank=True)
    q7_problem_solving = models.IntegerField(null=True, blank=True)
    q8_creativity = models.IntegerField(null=True, blank=True)
    q9_communication = models.IntegerField(null=True, blank=True)
    q10_detail_orientation = models.IntegerField(null=True, blank=True)

    q11_career_growth = models.IntegerField(null=True, blank=True)
    q12_recognition = models.IntegerField(null=True, blank=True)
    q13_entrepreneurship = models.IntegerField(null=True, blank=True)
    q14_learning = models.IntegerField(null=True, blank=True)
    q15_impact = models.IntegerField(null=True, blank=True)

    submitted_at = models.DateTimeField(default=timezone.now)

class Notification(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    jobseeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.jobseeker.full_name} applied to {self.job.title}"

class CVTip(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='cv_tips/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

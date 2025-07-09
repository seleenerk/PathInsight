from django.contrib import admin
from .models import (
    User,
    JobSeekerProfile,
    EmployerProfile,
    JobListing,
    CVAnalysis,
    SurveyResponse,
    JobApplication,
    MatchResult,
    JobPosting
)

admin.site.register(User)
admin.site.register(JobSeekerProfile)
admin.site.register(EmployerProfile)
admin.site.register(JobListing)
admin.site.register(CVAnalysis)
admin.site.register(SurveyResponse)
admin.site.register(JobApplication)
admin.site.register(MatchResult)
admin.site.register(JobPosting)


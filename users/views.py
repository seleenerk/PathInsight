# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import JobSeekerRegisterForm, EmployerRegisterForm, UserLoginForm, CVUploadForm, SurveyForm, JobPostingForm, ProfileUpdateForm, EmployerProfileForm
from .models import JobSeekerProfile, CVAnalysis, SurveyResponse, JobPosting, MatchResult, JobApplication, EmployerProfile, CVTip
from .cv_parser import extract_text_from_pdf, extract_email, extract_skills, extract_education, extract_experience, extract_certifications, extract_languages, parse_cv
import os
from .utils.matching import calculate_fuzzy_skill_match, extract_traits_from_text, calculate_trait_match 
import traceback 
from django.utils.timezone import now
from django.contrib import messages
from users.models import EmployerProfile, JobPosting, JobApplication, User, JobSeekerProfile
import logging
from django.core.exceptions import ObjectDoesNotExist
import random
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_staff:
                return redirect('users:admin_dashboard')
            elif user.role == 'jobseeker':
                return redirect('users:jobseeker_dashboard')
            elif user.role == 'employer':
                return redirect('users:employer_dashboard')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})

@never_cache
@login_required
def logout_view(request):
    logout(request)  
    request.session.flush() 
    response = redirect('users:login')  
    response.delete_cookie('sessionid')
    return response


def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'users/admin_login.html', {'error': 'Invalid credentials'})

    return render(request, 'users/admin_login.html')


@never_cache
@login_required
def jobseeker_dashboard(request):
    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)
    survey, _ = SurveyResponse.objects.get_or_create(user=request.user)
    analysis = CVAnalysis.objects.filter(user=request.user).first()

    all_jobs = JobPosting.objects.all()
    matched_job_ids = MatchResult.objects.filter(jobseeker=profile).values_list('job_id', flat=True)

    matched_jobs_raw = MatchResult.objects.filter(jobseeker=profile, job__isnull=False)
    trait_labels = {
        "q1_teamwork": "Teamwork",
        "q2_challenging_tasks": "Challenging Tasks",
        "q3_leadership": "Leadership",
        "q4_uncertainty": "Comfort with Uncertainty",
        "q5_stability": "Preference for Stability",
        "q6_technology_interest": "Interest in Technology",
        "q7_problem_solving": "Problem Solving",
        "q8_creativity": "Creativity",
        "q9_communication": "Communication",
        "q10_detail_orientation": "Attention to Detail",
        "q11_career_growth": "Career Growth Motivation",
        "q12_recognition": "Need for Recognition",
        "q13_entrepreneurship": "Entrepreneurial Spirit",
        "q14_learning": "Love for Learning",
        "q15_impact": "Desire to Make a Difference"
    }

    matched_jobs = []
    for match in matched_jobs_raw:
        explanation = match.explanation or ""
        for key, label in trait_labels.items():
            explanation = explanation.replace(key, label)

        matched_jobs.append({
            'job': match.job,
            'match_score': match.match_score,
            'explanation': explanation,
            'can_apply': match.match_score >= 50
        })

    matched_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    applied_jobs = JobApplication.objects.filter(jobseeker=profile)
    applied_job_ids = [app.job.id for app in applied_jobs]

    cv_uploaded = analysis is not None
    survey_completed = SurveyResponse.objects.filter(user=request.user).exists()

    answered = 0
    if survey:
        for field in survey._meta.fields:
            if field.name.startswith('q') and getattr(survey, field.name):
                answered += 1
    progress_percent = int((answered / 15) * 100)
    recent_applications = applied_jobs.order_by('-application_date')[:3]

    tips = [
        "Customize your CV for every role.",
        "Keep learning – growth is power.",
        "Confidence comes with preparation.",
        "Networking opens unexpected doors.",
        "You are closer than you think ✨",
    ]
    tip_of_the_day = random.choice(tips)

    experience_list = []
    skills_list = []
    certifications_list = []

    if analysis:
        if analysis.work_experience:
            experience_list = [exp.strip() for exp in analysis.work_experience.split('|') if exp.strip()]

        if analysis.skills:
            skills_list = [s.strip() for s in analysis.skills.split(',') if s.strip()]

        if analysis.certifications:
            certifications_list = [c.strip() for c in analysis.certifications.split('|') if c.strip()]

    if request.method == 'POST':
        if 'cv_file_path' in request.FILES:
            form = CVUploadForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                cv_file = request.FILES.get('cv_file_path')

                if not cv_file:
                    form.add_error('cv_file_path', 'Please select a file.')
                elif not cv_file.name.lower().endswith('.pdf'):
                    form.add_error('cv_file_path', 'Only PDF files are allowed.')
                elif cv_file.content_type != 'application/pdf':
                    form.add_error('cv_file_path', 'Invalid file type. Please upload a PDF.')
                else:
                    if profile.cv_file_path:
                        old_path = profile.cv_file_path.path
                        if os.path.isfile(old_path):
                            os.remove(old_path)

                    form.save()

                    if profile.cv_file_path:
                        parsed_data = parse_cv(profile.cv_file_path.path)
                        work_experience = parsed_data.get("experience", [])
                        experience_list = work_experience  

                        skills = parsed_data.get("skills", "")
                        skills_list = [s.strip() for s in skills.split(',') if s.strip()]

                        CVAnalysis.objects.update_or_create(
                            user=request.user,
                            defaults={
                                'email': parsed_data.get("email", ""),
                                'skills': skills,
                                'education': parsed_data.get("education", ""),
                                'certifications': parsed_data.get("certifications", ""),
                                'languages': parsed_data.get("languages", ""),
                                'work_experience': " | ".join(work_experience),
                                'experience_level': 'Intern',
                                'predicted_role': 'To be predicted'
                            }
                        )

                        profile.full_name = parsed_data.get("full_name", "")
                        profile.phone = parsed_data.get("phone", "")
                        profile.skills = skills
                        profile.education = parsed_data.get("education", "")
                        profile.work_experience = work_experience
                        profile.save()

                        email_from_cv = parsed_data.get("email", "")
                        if email_from_cv and email_from_cv != request.user.email:
                            request.user.email = email_from_cv
                            request.user.save()

                    messages.success(request, "CV uploaded and analyzed successfully!")
                    return redirect('users:jobseeker_dashboard')

        elif 'profile_picture' in request.FILES or 'full_name' in request.POST:
            form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('users:jobseeker_dashboard')

        else:
            SurveyResponse.objects.update_or_create(
                user=request.user,
                defaults={
                    'q1_teamwork': request.POST.get('q1'),
                    'q2_challenging_tasks': request.POST.get('q2'),
                    'q3_leadership': request.POST.get('q3'),
                    'q4_uncertainty': request.POST.get('q4'),
                    'q5_stability': request.POST.get('q5'),
                    'q6_technology_interest': request.POST.get('q6'),
                    'q7_problem_solving': request.POST.get('q7'),
                    'q8_creativity': request.POST.get('q8'),
                    'q9_communication': request.POST.get('q9'),
                    'q10_detail_orientation': request.POST.get('q10'),
                    'q11_career_growth': request.POST.get('q11'),
                    'q12_recognition': request.POST.get('q12'),
                    'q13_entrepreneurship': request.POST.get('q13'),
                    'q14_learning': request.POST.get('q14'),
                    'q15_impact': request.POST.get('q15'),
                }
            )
            messages.success(request, "Survey submitted successfully!")
            return redirect('users:jobseeker_dashboard')

    else:
        form = CVUploadForm(instance=profile)

    tips = CVTip.objects.order_by('-created_at')
    all_jobs = JobPosting.objects.select_related('employer').order_by('-created_at')
    return render(request, 'users/jobseeker_dashboard.html', {
        'profile': profile,
        'survey': survey,
        'analysis': analysis,
        'form': form,
        'all_jobs': all_jobs,
        'matched_job_ids': matched_job_ids,
        'matched_jobs': matched_jobs,
        'applied_job_ids': applied_job_ids,
        'cv_uploaded': cv_uploaded,
        'survey_completed': survey_completed,
        'answered': answered,
        'progress_percent': progress_percent,
        'recent_applications': recent_applications,
        'tip_of_the_day': tip_of_the_day,
        'tips': tips,
        'experience_list': experience_list,
        'skills_list': skills_list,
        'certifications_list': certifications_list,
    })


def register_employer(request):
    if request.method == 'POST':
        form = EmployerRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
    else:
        form = EmployerRegisterForm()
    return render(request, 'users/register_employer.html', {'form': form})


@never_cache
@login_required
def employer_dashboard(request):
    employer_profile = get_object_or_404(EmployerProfile, user=request.user)
    employer = EmployerProfile.objects.get(user=request.user)
    form = EmployerProfileForm(request.POST or None, instance=employer)

    if request.method == 'POST' and 'company_name' in request.POST:
        if form.is_valid():
            form.save()
            messages.success(request, "Company profile updated!")
            return redirect('users:employer_dashboard')

    # AUTO-FILL için initial data
    initial_data = {
        'company_name': employer_profile.company_name,
        'industry': employer_profile.industry,
        'founded_year': employer_profile.founded_year,
        'location': employer_profile.location,
    }

    job_posting_form = JobPostingForm(initial=initial_data)

    job_posts = JobPosting.objects.filter(employer=employer_profile).select_related('employer').order_by('-created_at')

    for job in job_posts:
        job.applications_list = JobApplication.objects.filter(job=job).select_related('jobseeker__user')

    total_job_posts = job_posts.count()
    total_applications = JobApplication.objects.filter(job__in=job_posts).count()
    last_job = job_posts.first() if total_job_posts > 0 else None

    return render(request, 'users/employer_dashboard.html', {
        'employer': employer,
        'form': form,
        'job_posting_form': job_posting_form,
        'job_posts': job_posts,
        'total_job_posts': total_job_posts,
        'total_applications': total_applications,
        'last_job': last_job,
    })


def register_jobseeker(request):
    if request.method == 'POST':
        form = JobSeekerRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
    else:
        form = JobSeekerRegisterForm()
    return render(request, 'users/register_jobseeker.html', {'form': form})

@never_cache
@login_required
def delete_cv_view(request):
    profile = JobSeekerProfile.objects.get(user=request.user)

    if profile.cv_file_path:
        old_path = profile.cv_file_path.path
        if os.path.isfile(old_path):
            os.remove(old_path)
        profile.cv_file_path = None
        profile.save()

    CVAnalysis.objects.filter(user=request.user).delete()

    return redirect('users:jobseeker_dashboard')

@never_cache
@login_required
def survey_view(request):
    user = request.user
    try:
        survey = SurveyResponse.objects.get(user=user)
    except SurveyResponse.DoesNotExist:
        survey = None

    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            response = form.save(commit=False)
            response.user = user
            response.save()
            return redirect('users:jobseeker_dashboard')
    else:
        form = SurveyForm(instance=survey)

    return render(request, 'users/survey.html', {'form': form})

@never_cache
@login_required
def create_job_posting(request):
    if request.method == 'POST':
        employer_profile = EmployerProfile.objects.get(user=request.user)
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.employer = employer_profile
            job_posting.save()
            return redirect('users:employer_dashboard') 
    else:
        form = JobPostingForm()
    return render(request, 'users/create_job_posting.html', {'form': form})

@never_cache
@login_required
def edit_job_posting(request, pk):
    employer_profile = EmployerProfile.objects.get(user=request.user)
    job = get_object_or_404(JobPosting, pk=pk, employer=employer_profile)

    job_posts = JobPosting.objects.filter(employer=employer_profile)
    for j in job_posts:
        j.applications_list = JobApplication.objects.filter(job=j).select_related('jobseeker__user')

    if request.method == 'POST' and 'edit' in request.POST:
 
        job_posting_form = JobPostingForm(instance=job)
        return render(request, 'users/employer_dashboard.html', {
            'form': EmployerProfileForm(instance=employer_profile),
            'job_posting_form': job_posting_form,
            'job_posts': job_posts,
            'edit_job_id': job.id,
            'total_job_posts': job_posts.count(),
            'total_applications': JobApplication.objects.filter(job__in=job_posts).count(),
            'last_job': job_posts.order_by('-created_at').first()
        })

    elif request.method == 'POST':

        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
        return redirect('users:employer_dashboard')

    return redirect('users:employer_dashboard')


@never_cache
@login_required
def job_listings_view(request):
    user = request.user
    jobseeker_profile = JobSeekerProfile.objects.get(user=user)

    all_jobs = JobPosting.objects.all()

    matched_job_ids = MatchResult.objects.filter(jobseeker=jobseeker_profile).values_list('job_id', flat=True)

    return render(request, 'users/job_listings.html', {
        'all_jobs': all_jobs,
        'matched_job_ids': matched_job_ids
    })

@never_cache
@login_required
def apply_job_view(request, job_id):
    user = request.user
    job = get_object_or_404(JobPosting, id=job_id)
    jobseeker_profile = JobSeekerProfile.objects.get(user=user)

    is_matched = MatchResult.objects.filter(jobseeker=jobseeker_profile, job=job).exists()

    if request.method == 'POST' and is_matched:
        already_applied = JobApplication.objects.filter(jobseeker=jobseeker_profile, job=job).exists()
        if not already_applied:
            JobApplication.objects.create(jobseeker=jobseeker_profile, job=job)

    return redirect('users:jobseeker_dashboard')


@never_cache
@login_required
def start_matching(request):
    try:
        user = request.user
        profile = JobSeekerProfile.objects.get(user=user)
        cv = CVAnalysis.objects.filter(user=user).first()
        survey = SurveyResponse.objects.filter(user=user).first()

        if not cv or not survey:
            messages.error(request, "Please upload CV and complete survey.")
            return redirect('users:jobseeker_dashboard')

        cv_skills = [s.strip() for s in (cv.skills or "").split(',') if s.strip()]

        user_answers = {
            "q1_teamwork": survey.q1_teamwork,
            "q2_challenging_tasks": survey.q2_challenging_tasks,
            "q3_leadership": survey.q3_leadership,
            "q4_uncertainty": survey.q4_uncertainty,
            "q5_stability": survey.q5_stability,
            "q6_technology_interest": survey.q6_technology_interest,
            "q7_problem_solving": survey.q7_problem_solving,
            "q8_creativity": survey.q8_creativity,
            "q9_communication": survey.q9_communication,
            "q10_detail_orientation": survey.q10_detail_orientation,
            "q11_career_growth": survey.q11_career_growth,
            "q12_recognition": survey.q12_recognition,
            "q13_entrepreneurship": survey.q13_entrepreneurship,
            "q14_learning": survey.q14_learning,
            "q15_impact": survey.q15_impact,
        }

        for job in JobPosting.objects.all():

            job_skills = [s.strip() for s in (job.required_skills or "").split(',') if s.strip()]

            skill_score, matched_skills = calculate_fuzzy_skill_match(cv_skills, job_skills)
      

            matched_traits_keys = extract_traits_from_text(job.preferred_traits or "")
            trait_score = calculate_trait_match(user_answers, matched_traits_keys)
            final_score = round((0.75 * skill_score + 0.25 * trait_score), 2)

            explanation = ""
            if matched_skills:
                explanation += f"Skills matched: {', '.join(matched_skills)}. "
            if matched_traits_keys:
                explanation += f"Traits matched: {', '.join(matched_traits_keys)}."
            if not explanation:
                explanation = "No strong matches found, but this job was evaluated."

            MatchResult.objects.update_or_create(
                jobseeker=profile,
                job=job,
                defaults={
                    'match_score': final_score,
                    'explanation': explanation,
                    'matched_skills': ", ".join(matched_skills),
                    'matched_traits': ", ".join(matched_traits_keys),
                }
            )

        return redirect('users:jobseeker_dashboard')

    except Exception as e:
        return redirect('users:jobseeker_dashboard')

@never_cache
@login_required
def update_employer_profile(request):
    profile = EmployerProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('users:employer_dashboard')
    else:
        form = EmployerProfileForm(instance=profile)

    return render(request, 'users/employer_dashboard.html', {
        'form': form,
        'employer': profile, 
        'job_posts': JobPosting.objects.filter(employer=profile),
        'applications': JobApplication.objects.all(),
    })

@never_cache
@login_required
def update_jobseeker_profile(request):
    profile = JobSeekerProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('users:jobseeker_dashboard')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'users/jobseeker_dashboard.html', {
        'form': form,
        'profile': profile
    })


@never_cache
@user_passes_test(lambda u: u.is_staff)
@login_required
def admin_dashboard(request):
    jobseekers = JobSeekerProfile.objects.filter(user__role='jobseeker')
    employers = EmployerProfile.objects.filter(user__role='employer')
    job_postings = JobPosting.objects.all().order_by('-created_at')
    total_seekers = jobseekers.count()
    total_employers = employers.count()
    total_jobs = job_postings.count()
    total_applications = JobApplication.objects.count()

    return render(request, 'users/admin_dashboard.html', {
        'jobseekers': jobseekers,
        'employers': employers,
        'job_postings': job_postings,
        'total_seekers': total_seekers,
        'total_employers': total_employers,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
    })

@require_POST
@user_passes_test(lambda u: u.is_staff)
def delete_jobseeker(request, pk):
    profile = get_object_or_404(JobSeekerProfile, pk=pk)
    user = profile.user
    profile.delete()
    user.delete()
    messages.success(request, "Job Seeker deleted.")
    return redirect('users:admin_dashboard')

@require_POST
@user_passes_test(lambda u: u.is_staff)
def delete_employer(request, pk):
    profile = get_object_or_404(EmployerProfile, pk=pk)
    user = profile.user
    profile.delete()
    user.delete()
    messages.success(request, "Employer deleted.")
    return redirect('users:admin_dashboard')

@never_cache
@login_required
@require_POST
def delete_job_posting(request, pk):
    job = get_object_or_404(JobPosting, pk=pk)

    if request.user.is_staff or job.employer.user == request.user:
 
        MatchResult.objects.filter(job=job).delete()
        JobApplication.objects.filter(job=job).delete()
        job.delete()
        messages.success(request, "Job Posting deleted.")
        
        if request.user.is_staff:
            return redirect('users:admin_dashboard')
        else:
            return redirect('users:employer_dashboard')
    else:
        messages.error(request, "You do not have permission to delete this job.")
        return redirect('users:employer_dashboard')

@never_cache
@login_required
def view_applicant_profile(request, applicant_id):
    applicant = get_object_or_404(JobSeekerProfile, id=applicant_id)
    
    try:
        cv = CVAnalysis.objects.get(user=applicant.user)
    except CVAnalysis.DoesNotExist:
        cv = None

    return render(request, 'users/view_applicant_profile.html', {
        'applicant': applicant,
        'cv': cv,
    })

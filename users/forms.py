from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, JobSeekerProfile, EmployerProfile, JobPosting, SurveyResponse
from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class JobSeekerRegisterForm(UserCreationForm):
    full_name = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'jobseeker'
        if commit:
            user.save()
            JobSeekerProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
            )
        return user

class EmployerRegisterForm(UserCreationForm):
    company_name = forms.CharField()
    company_description = forms.CharField(widget=forms.Textarea)
    website = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'employer'
        if commit:
            user.save()
            EmployerProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                company_description=self.cleaned_data['company_description'],
                website=self.cleaned_data.get('website'),
            )
        return user

class CVUploadForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['cv_file_path']


LIKERT_CHOICES = [
    (1, 'Strongly Disagree'),
    (2, 'Disagree'),
    (3, 'Neutral'),
    (4, 'Agree'),
    (5, 'Strongly Agree'),
]

class SurveyForm(forms.ModelForm):
    q1_teamwork = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I enjoy working in a team.")
    q2_challenging_tasks = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I like taking on challenging tasks.")
    q3_leadership = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I prefer to take the lead in decision-making processes.")
    q4_uncertainty = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="Uncertainty makes me uncomfortable.")
    q5_stability = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I would like to stay in the same job for a long time.")
    q6_technology_interest = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I am interested in new technologies.")
    q7_problem_solving = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I find problem-solving enjoyable.")
    q8_creativity = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I enjoy tasks that require creative thinking.")
    q9_communication = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I enjoy communicating with people.")
    q10_detail_orientation = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I pay attention to details.")
    q11_career_growth = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I want to advance quickly in my career.")
    q12_recognition = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="Being appreciated at work is important to me.")
    q13_entrepreneurship = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I have goals such as starting my own business.")
    q14_learning = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I enjoy learning new things.")
    q15_impact = forms.ChoiceField(choices=LIKERT_CHOICES, widget=forms.RadioSelect, label="I want to work in a job where I can make a difference.")

    class Meta:
        model = SurveyResponse
        fields = [
            'q1_teamwork', 'q2_challenging_tasks', 'q3_leadership',
            'q4_uncertainty', 'q5_stability', 'q6_technology_interest',
            'q7_problem_solving', 'q8_creativity', 'q9_communication',
            'q10_detail_orientation', 'q11_career_growth', 'q12_recognition',
            'q13_entrepreneurship', 'q14_learning', 'q15_impact'
        ]

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'required_skills', 'preferred_traits', 'company_name', 'industry', 'founded_year', 'location']
        help_texts = {
            'required_skills': 'Enter as comma-separated values.',
            'preferred_traits': "Describe the personal traits or soft skills you're looking for (e.g. teamwork, creativity, attention to detail).",
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['full_name', 'phone', 'email','skills', 'linkedin', 'education', 'work_experience', 'profile_picture']
        widgets = {
            'education': forms.Textarea(attrs={'rows': 3}),
            'work_experience': forms.Textarea(attrs={'rows': 3}),
        }

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = [
            'company_name',
            'company_description',
            'website',
            'industry',
            'company_size',
            'founded_year',
            'location',
            'contact_email',
            'linkedin_url',
        ]






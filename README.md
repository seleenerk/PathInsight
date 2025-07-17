# PathInsight

**PathInsight** is a Django-based CV analysis and job matching platform that bridges the gap between job seekers and employers.  
It uses Natural Language Processing (NLP) techniques to extract key information such as email, phone number, education, skills, work experience, certifications, and languages from PDF resumes.  
This data is then matched with job postings and personality traits to recommend the most relevant positions to each user.

---

## 🚀 Features

- Automatic PDF resume parsing using PyMuPDF + regex-based NLP
- Extraction of skills, education, experience, certifications, and languages
- 15-question Likert-scale personality assessment
- Job matching based on Fuzzy Matching and Trait Scoring
- Separate dashboards for job seekers and employers
- Django-based authentication and admin panel
- Admin dashboard with job/user statistics and management tools

---

## 🛠️ Technologies

- **Backend:** Python 3, Django
- **Frontend:** HTML, CSS, JavaScript (within Django templates)
- **NLP:** PyMuPDF, Regular Expressions, rule-based information extraction
- **Matching Algorithm:** Fuzzy string matching + personality trait analysis
- **Database:** SQLite (default), PostgreSQL (optional)

---

## 👥 User Roles

Job Seeker: Registers → Uploads CV → Completes survey → Gets matched → Applies to jobs

Employer: Registers → Posts jobs → Views and manages applicants

Admin: Manages all users, jobs, and application data via admin dashboard

---

## 📁 Project Structure (Summary)
```plaintext
users/
├── models.py           # Data models for users, CVs, jobs, applications
├── views.py            # Auth, dashboards, CV parsing, job matching
├── forms.py            # Registration, login, CV upload, survey forms
├── cv_parser.py        # Rule-based NLP to extract CV data
├── utils/matching.py   # Matching logic (skills + traits)
├── templates/users/    # HTML templates
```

---

## 🔍 Sample CV Parsing Output
```json
{
  "email": "example@gmail.com",
  "phone": "+90 555 123 4567",
  "skills": "Python, Django, SQL",
  "education": "BSc in Computer Engineering | XYZ University",
  "certifications": "Python for Everybody - Coursera",
  "languages": "English, Turkish",
  "experience": [
    "Software Intern at ABC Inc - 2022",
    "Freelance Web Developer - 2021"
  ]
}
```

---

## 🧠 Matching Logic
Fuzzy Matching: Calculates similarity between extracted skills and required job skills

Trait Matching: Compares the job seeker's survey results with employer's desired traits

Final Score Formula:
match_score = 0.75 * skill_score + 0.25 * trait_score

---

## 📦 Installation

```bash
git clone https://github.com/seleenerk/PathInsight.git
cd PathInsight
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

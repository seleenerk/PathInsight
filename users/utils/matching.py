from fuzzywuzzy import fuzz
from users.models import JobPosting, CVAnalysis, SurveyResponse, MatchResult, JobSeekerProfile

def calculate_fuzzy_skill_match(cv_skills, job_required_skills):
    if not cv_skills or not job_required_skills:
        print("No skills provided for matching.", flush=True)
        return 0.0, []

    match_scores = []
    matched_skills = []


    for job_skill in job_required_skills:
        best_match_score = 0
        best_cv_skill = None

        for cv_skill in cv_skills:
            score = fuzz.token_set_ratio(job_skill.lower(), cv_skill.lower())
            if score > best_match_score:
                best_match_score = score
                best_cv_skill = cv_skill

        if best_match_score >= 45 and best_cv_skill:
            matched_skills.append(best_cv_skill)
            match_scores.append(best_match_score)
        else:
            match_scores.append(0)

    average_score = sum(match_scores) / len(job_required_skills)

    return round(average_score, 2), matched_skills

def extract_traits_from_text(text):
    text = text.lower()
    traits = []

    mapping = {
        "q1_teamwork": [
            "teamwork", "collaborate", "team player", "work well with others", "cooperate"
        ],
        "q2_challenging_tasks": [
            "challenging", "take on challenges", "difficult tasks", "complex problems", "ambitious"
        ],
        "q3_leadership": [
            "lead", "leadership", "take initiative", "manage", "supervise", "guiding others"
        ],
        "q4_uncertainty": [
            "uncertain", "ambiguity", "adaptable", "handle the unexpected", "flexible in situations"
        ],
        "q5_stability": [
            "stability", "long-term", "stay in a position", "committed", "consistent"
        ],
        "q6_technology_interest": [
            "technology", "tech-savvy", "interested in tech", "new technologies", "tech driven"
        ],
        "q7_problem_solving": [
            "problem-solving", "solve problems", "analytical", "critical thinking", "troubleshooting"
        ],
        "q8_creativity": [
            "creative", "creativity", "think outside the box", "innovative", "original ideas"
        ],
        "q9_communication": [
            "communicate", "communication", "clear communicator", "interpersonal", "communicates well", "written and verbal"
        ],
        "q10_detail_orientation": [
            "attention to detail", "detail-oriented", "precise", "accuracy", "meticulous", "thorough"
        ],
        "q11_career_growth": [
            "career growth", "advance quickly", "promotion", "career oriented", "development focused"
        ],
        "q12_recognition": [
            "recognition", "appreciated", "acknowledged", "rewarded", "being valued"
        ],
        "q13_entrepreneurship": [
            "entrepreneur", "startup", "build my own", "founder", "entrepreneurial"
        ],
        "q14_learning": [
            "learn", "eager to learn", "curious", "learning new things", "continuous learner", "open to learning"
        ],
        "q15_impact": [
            "make a difference", "impact", "change the world", "positive change", "meaningful work"
        ]
    }

    for trait_key, keywords in mapping.items():
        for keyword in keywords:
            if keyword in text:
                traits.append(trait_key)
                break  

    return traits

def calculate_trait_match(user_survey: dict, matched_traits: list):
    if not matched_traits:
        print("No traits matched from CV.", flush=True)
        return 0.0

    total_score = 0
    for trait in matched_traits:
        answer = user_survey.get(trait, 0)
        print(f"[TRAIT SCORE] Trait: {trait} → User Answer: {answer}", flush=True)
        total_score += answer

    max_score = len(matched_traits) * 5
    trait_match_score = (total_score / max_score) * 100
    return round(trait_match_score, 2)


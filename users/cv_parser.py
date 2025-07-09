import fitz  # PyMuPDF
import re

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else "Not Found"

def extract_skills(text):
    skill_keywords = [
        # Programming Languages
        'Python', 'Java', 'C++', 'C#', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin',
        'Assembly', 'Perl', 'Scala', 'Dart', 'R', 'Haskell',

        # Web & App Development
        'HTML', 'CSS', 'SASS', 'LESS', 'React', 'Vue.js', 'Angular', 'Next.js', 'Nuxt.js', 'Bootstrap', 'Tailwind',
        'Node.js', 'Express.js', 'Laravel', 'Spring', 'Flask', 'Django', 'ASP.NET', 'jQuery', 'Redux',

        # Mobile
        'React Native', 'Flutter', 'SwiftUI', 'Android SDK', 'Xamarin', 'iOS',

        # Databases
        'SQL', 'PostgreSQL', 'MySQL', 'MariaDB', 'MongoDB', 'Redis', 'Cassandra', 'Oracle', 'SQLite', 'DynamoDB',

        # Data Science & AI
        'Data Analysis', 'Data Visualization', 'Machine Learning', 'Deep Learning', 'Supervised Learning',
        'Unsupervised Learning', 'Classification', 'Regression', 'Clustering', 'Recommendation Systems',
        'TensorFlow', 'Keras', 'PyTorch', 'Scikit-learn', 'XGBoost', 'LightGBM', 'OpenCV',

        # Libraries
        'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'NLTK', 'SpaCy', 'StatsModels', 'SymPy', 'Gensim', 'Plotly',

        # DevOps & Cloud
        'Git', 'GitHub', 'GitLab', 'Docker', 'Kubernetes', 'Jenkins', 'Ansible', 'Terraform', 'CircleCI',
        'AWS', 'Azure', 'GCP', 'CloudFormation', 'EC2', 'S3', 'Lambda', 'Firebase', 'Heroku', 'Netlify', 'Vercel',

        # Monitoring & Observability
        'Prometheus', 'Grafana', 'Datadog', 'New Relic', 'Zabbix', 'ELK Stack', 'Splunk', 'Graylog',

        # Container & Infrastructure
        'Helm', 'Istio', 'Consul', 'Nginx', 'Apache', 'HAProxy', 'Vagrant', 'VirtualBox', 'VMware',

        # Scripting
        'Shell Scripting', 'Bash', 'Zsh', 'PowerShell', 'Makefile', 'Crontab',

        # Project & Workflow Tools
        'JIRA', 'Trello', 'Asana', 'Notion', 'Slack', 'Confluence', 'Figma', 'Miro', 'Draw.io',

        # Build & Package Tools
        'Webpack', 'Rollup', 'Parcel', 'Babel', 'npm', 'Yarn', 'pnpm', 'Gradle', 'Maven', 'Make', 'CMake',

        # APIs
        'REST API', 'GraphQL', 'gRPC', 'WebSocket', 'OAuth2', 'JWT',

        # Testing
        'Unit Testing', 'Integration Testing', 'Selenium', 'Cypress', 'Jest', 'Mocha', 'Pytest', 'Postman',

        # Security & Network
        'Wireshark', 'Nmap', 'Burp Suite', 'Metasploit', 'Snort', 'SSL', 'TLS', 'Firewalls', 'OSINT',

        # CMS / Digital
        'WordPress', 'Google Analytics', 'SEO', 'SEM', 'Content Writing', 'Power BI', 'Tableau',

        # Engineering Tools
        'MATLAB', 'Simulink', 'SolidWorks', 'AutoCAD', 'Fusion 360', 'CATIA', 'Siemens NX', 'ANSYS', 'HyperMesh',
        'STA4CAD', 'SAP2000', 'ETABS', 'Tekla Structures', 'Primavera P6', 'Civil 3D', 'Revit', 'SketchUp',
        'LTspice', 'OrCAD', 'KiCad', 'Multisim', 'PLC Programming', 'G-code', 'CNC Programming', 'Excel'
    ]

    found_skills = []
    for skill in skill_keywords:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return ", ".join(found_skills) if found_skills else "Not Found"

def extract_education(text):
    lines = text.splitlines()
    education_headers = ["Education", "Educational Background", "Academic Background"]
    end_headers = ["Experience", "Skills", "Certifications", "Languages", "Projects"]

    start_idx = -1
    end_idx = len(lines)
    
    for i, line in enumerate(lines):
        if any(header.lower() in line.lower() for header in education_headers):
            start_idx = i + 1
            break

    if start_idx == -1:
        return "Not Found"

    for i in range(start_idx, len(lines)):
        if any(end.lower() in lines[i].lower() for end in end_headers):
            end_idx = i
            break

    education_lines = lines[start_idx:end_idx]
    
    final = []
    for line in education_lines:
        line = line.strip()
        if line and not any(word in line.lower() for word in [
            "english", "turkish", "german", "fluent", "native", "intermediate"
        ]):
            final.append(line)

    return " | ".join(final) if final else "Not Found"

def extract_experience(text):
    lines = text.splitlines()
    experience_headers = ["Experience", "Work Experience", "Professional Experience", "Employment History", "Internships"]
    end_headers = ["Education", "Skills", "Certifications", "Languages", "Projects"]

    start_idx = -1
    end_idx = len(lines)

    for i, line in enumerate(lines):
        if any(header.lower() in line.lower() for header in experience_headers):
            start_idx = i + 1
            break

    if start_idx == -1:
        return []

    for i in range(start_idx, len(lines)):
        if any(end.lower() in lines[i].lower() for end in end_headers):
            end_idx = i
            break

    experience_lines = lines[start_idx:end_idx]
    entries = []

    i = 0
    while i < len(experience_lines):
        block = experience_lines[i].strip()

        if " at " in block and re.search(r"\d{4}", block):
            entries.append(block)
            i += 1

        elif i + 2 < len(experience_lines):
            role = experience_lines[i].strip()
            company = experience_lines[i+1].strip()
            dates = experience_lines[i+2].strip()
            if role and company and dates:
                entries.append(f"{role} at {company} - {dates}")
                i += 3
            else:
                i += 1
        else:
            i += 1
    return entries

def extract_certifications(text):
    cert_keywords = ['certificate', 'certified', 'certification', 'udemy', 'coursera', 'edx']
    unwanted_headers = ['certifications', 'sertifikalar', 'certification'] 
    lines = text.splitlines()
    found = []

    for line in lines:
        line_clean = line.strip("•-–| ").strip()
        line_lower = line_clean.lower()

        if any(line_lower == h for h in unwanted_headers):
            continue
        if any(keyword in line_lower for keyword in cert_keywords):
            found.append(line_clean)

    return " | ".join(found) if found else "Not Found"

def extract_languages(text):
    lines = text.splitlines()
    languages = [
        'Turkish', 'English', 'German', 'French', 'Spanish',
        'Italian', 'Arabic', 'Russian', 'Japanese', 'Chinese'
    ]
    found = set()

    start = -1
    for i, line in enumerate(lines):
        if "language" in line.lower():
            start = i + 1
            break

    if start != -1:

        for line in lines[start:]:
            if any(stop in line.lower() for stop in ["skills", "certifications", "education", "experience"]):
                break
            for lang in languages:
                if lang.lower() in line.lower():
                    found.add(lang)

    if not found:
        for lang in languages:
            if lang.lower() in text.lower():
                found.add(lang)

    return ", ".join(sorted(found)) if found else "Not Found"

def extract_phone(text):
    pattern = r'(\+90[\s\-]?)?\(?0?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
    match = re.search(pattern, text)
    return match.group(0) if match else "Not Found"


def parse_cv(file_path):
    text = extract_text_from_pdf(file_path)
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "certifications": extract_certifications(text),
        "languages": extract_languages(text),
        "experience": extract_experience(text),
    }


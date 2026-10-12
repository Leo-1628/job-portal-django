# 💼 Job Portal - Django 

A complete Job Portal website built with Django where Companies can post jobs and Candidates can apply with OTP email verification.

🔗 **Live Repo:** https://github.com/Leo-1628/job-portal-django

---

### 🚀 Features

**For Candidates:**
- User Registration with OTP Email Verification
- Browse & Search Jobs by Title, Location, Skills
- Apply for Jobs, Upload Resume
- Track My Applications
- Profile Management

**For Companies:**
- Company Dashboard
- Post New Jobs
- View My Posted Jobs (my_jobs.html)
- View Applicants for each job
- Delete Jobs

**For Admin:**
- Django Admin Panel to manage all Jobs, Users, Applications

---

### 🛠️ Tech Stack

- **Backend:** Python, Django 5.x
- **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
- **Database:** SQLite3 (can be migrated to PostgreSQL/MySQL)
- **Auth:** OTP Email Verification using Django Email
- **Icons:** FontAwesome

---

### 📂 Project Structureapp/ - Main app (models, views, urls)
project/ - Settings & main urls
static/ - CSS, JS, Images
templates/ - All HTML pages (my_jobs, job_listings etc)
manage.pyjavascript
---

### ⚙️ How to Run Locally

```bash
# Clone
git clone https://github.com/Leo-1628/job-portal-django.git
cd job-portal-django

# Create venv
python -m venv myvenv
myvenv\Scripts\activate  # Windows

# Install
pip install django

# Run migrations
python manage.py migrate

# Run server
python manage.py runserverThen open 127.0.0.1:8000
👨‍💻 Developed By
Leosiva (Leo-1628) - Chennai, India
Python | Django | GitHub
📧 leo.s161028@gmail.com
⭐ Star this repo if you like it!javascript
**3. Save file (Ctrl+S)**

**4. Then in terminal run:**

```bash
git add README.md
git commit -m "Add professional README"
git push
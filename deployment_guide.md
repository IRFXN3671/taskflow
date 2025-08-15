# Task Tracker - Windows Deployment Guide

## Prerequisites

### 1. Install Python
Download and install Python 3.11 or later from https://python.org
- During installation, check "Add Python to PATH"
- Verify installation: `python --version`

### 2. Install PostgreSQL
Download PostgreSQL from https://www.postgresql.org/download/windows/
- Remember the password you set for the 'postgres' user
- Default port is 5432

## Step-by-Step Deployment Commands

### Step 1: Clone or Download Project
```cmd
# If using Git
git clone <your-repository-url>
cd task_tracker

# Or download and extract the project files to a folder
cd C:\path\to\task_tracker
```

### Step 2: Create Virtual Environment
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```cmd
pip install flask flask-sqlalchemy psycopg2-binary gunicorn werkzeug
```

### Step 4: Set Up Database
```cmd
# Connect to PostgreSQL (replace 'your_password' with your postgres password)
psql -U postgres -h localhost

# In the PostgreSQL prompt, create database:
CREATE DATABASE task_tracker;
CREATE USER task_user WITH PASSWORD 'secure_password123';
GRANT ALL PRIVILEGES ON DATABASE task_tracker TO task_user;
\q
```

### Step 5: Configure Environment Variables
Create a file named `.env` in your project folder:
```
SESSION_SECRET=your_secret_key_here_make_it_long_and_random
DATABASE_URL=postgresql://task_user:secure_password123@localhost:5432/task_tracker
```

### Step 6: Initialize Database Tables
```cmd
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database tables created!')"
```

### Step 7: Create Sample Users (Optional)
```cmd
python -c "
from app import app, db
from models import User
with app.app_context():
    manager = User()
    manager.username = 'admin'
    manager.email = 'admin@company.com'
    manager.first_name = 'Admin'
    manager.last_name = 'User'
    manager.role = 'manager'
    manager.department = 'Management'
    manager.set_password('admin123')
    
    employee = User()
    employee.username = 'employee'
    employee.email = 'employee@company.com'
    employee.first_name = 'Test'
    employee.last_name = 'Employee'
    employee.role = 'employee'
    employee.department = 'Development'
    employee.set_password('emp123')
    
    db.session.add_all([manager, employee])
    db.session.commit()
    print('Sample users created!')
    print('Manager: username=admin, password=admin123')
    print('Employee: username=employee, password=emp123')
"
```

### Step 8: Run the Application

#### For Development:
```cmd
python main.py
```

#### For Production (using Gunicorn):
```cmd
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

### Step 9: Access the Application
Open your web browser and go to:
- http://localhost:5000

## Windows Service Setup (Optional)

To run as a Windows service, install NSSM (Non-Sucking Service Manager):

### Step 1: Download NSSM
Download from https://nssm.cc/download

### Step 2: Install Service
```cmd
nssm install TaskTracker
```
- Path: `C:\path\to\your\venv\Scripts\python.exe`
- Startup directory: `C:\path\to\task_tracker`
- Arguments: `main.py`

### Step 3: Start Service
```cmd
nssm start TaskTracker
```

## Troubleshooting

### Database Connection Issues:
```cmd
# Test database connection
python -c "import psycopg2; conn = psycopg2.connect('postgresql://task_user:secure_password123@localhost:5432/task_tracker'); print('Database connection successful!'); conn.close()"
```

### Port Already in Use:
```cmd
# Find process using port 5000
netstat -ano | findstr :5000
# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Environment Variables Not Loading:
Install python-dotenv and load .env file:
```cmd
pip install python-dotenv
```

Add to main.py:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Security Notes

1. Change default passwords in production
2. Use strong SESSION_SECRET (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
3. Configure firewall to restrict database access
4. Use HTTPS in production with proper SSL certificates
5. Regular database backups

## Default Login Credentials

After running Step 7:
- **Manager**: username=admin, password=admin123
- **Employee**: username=employee, password=emp123

Change these passwords after first login!
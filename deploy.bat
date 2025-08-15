@echo off
echo ====================================
echo Task Tracker - Windows Deployment
echo ====================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

echo Step 2: Activating virtual environment...
call venv\Scripts\activate

echo Step 3: Installing dependencies...
pip install flask flask-sqlalchemy psycopg2-binary gunicorn werkzeug python-dotenv

echo Step 4: Setting up environment variables...
if not exist ".env" (
    echo SESSION_SECRET=your_secret_key_change_this_in_production > .env
    echo DATABASE_URL=postgresql://task_user:secure_password123@localhost:5432/task_tracker >> .env
    echo.
    echo Created .env file - Please update DATABASE_URL with your PostgreSQL credentials
)

echo Step 5: Creating database tables...
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database tables created!')"

echo Step 6: Creating sample users...
python -c "
from app import app, db
from models import User
import sys
with app.app_context():
    # Check if users already exist
    if User.query.count() > 0:
        print('Users already exist, skipping user creation')
        sys.exit(0)
    
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
"

echo.
echo ====================================
echo Deployment Complete!
echo ====================================
echo.
echo Login Credentials:
echo Manager: username=admin, password=admin123
echo Employee: username=employee, password=emp123
echo.
echo To start the application, run:
echo python main.py
echo.
echo Then open http://localhost:5000 in your browser
echo.
pause
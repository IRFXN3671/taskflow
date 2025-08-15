@echo off
echo ========================================
echo Task Tracker - Quick Setup for Windows
echo ========================================
echo.

echo Step 1: Creating .env file...
if not exist ".env" (
    (
        echo # Task Tracker Environment Configuration
        echo.
        echo # Session secret key for Flask sessions
        echo SESSION_SECRET=your_secret_key_here_change_this_in_production
        echo.
        echo # Database connection URL
        echo # For PostgreSQL: postgresql://username:password@localhost:5432/database_name
        echo # For SQLite ^(development^): sqlite:///task_tracker.db
        echo DATABASE_URL=sqlite:///task_tracker.db
    ) > .env
    echo Created .env file with SQLite database for quick testing
) else (
    echo .env file already exists
)

echo.
echo Step 2: Installing required package...
pip install python-dotenv

echo.
echo Step 3: Testing the application...
python main.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo The application should now be running with SQLite database.
echo Open http://localhost:5000 in your browser.
echo.
echo Default login credentials:
echo Manager: username=manager, password=password123
echo Employee: username=employee1, password=password123
echo.
echo To use PostgreSQL instead:
echo 1. Install PostgreSQL
echo 2. Edit .env file and change DATABASE_URL
echo 3. Restart the application
echo.
pause
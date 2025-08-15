#!/usr/bin/env python3
"""
Command-line script to add users and managers to the Task Tracker application
Usage: python add_user.py
"""

from app import app, db
from models import User

def add_user_interactive():
    """Interactive script to add a new user"""
    print("=" * 50)
    print("Task Tracker - Add New User")
    print("=" * 50)
    
    with app.app_context():
        print("\nEnter user details:")
        
        # Get user input
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            print(f"❌ Error: Username '{username}' already exists!")
            return False
            
        if User.query.filter_by(email=email).first():
            print(f"❌ Error: Email '{email}' already exists!")
            return False
        
        # Role selection
        print("\nRole options:")
        print("1. Employee")
        print("2. Manager")
        role_choice = input("Select role (1 or 2): ").strip()
        
        if role_choice == "2":
            role = "manager"
        else:
            role = "employee"
        
        department = input("Department (optional): ").strip() or None
        password = input("Password (min 6 characters): ").strip()
        
        if len(password) < 6:
            print("❌ Error: Password must be at least 6 characters!")
            return False
        
        # Create new user
        try:
            new_user = User()
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.username = username
            new_user.email = email
            new_user.role = role
            new_user.department = department
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"\n✅ Success! User '{new_user.full_name}' added successfully!")
            print(f"   Username: {username}")
            print(f"   Role: {role.title()}")
            print(f"   Email: {email}")
            print(f"   Department: {department or 'N/A'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating user: {str(e)}")
            db.session.rollback()
            return False

def list_existing_users():
    """List all existing users"""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in the database.")
            return
        
        print("\n" + "=" * 80)
        print("EXISTING USERS")
        print("=" * 80)
        print(f"{'Name':<25} {'Username':<15} {'Email':<30} {'Role':<10}")
        print("-" * 80)
        
        for user in users:
            print(f"{user.full_name:<25} {user.username:<15} {user.email:<30} {user.role.title():<10}")

def main():
    print("\nTask Tracker User Management")
    print("=" * 30)
    print("1. Add new user")
    print("2. List existing users")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        add_user_interactive()
        
        # Ask if they want to add another user
        while input("\nAdd another user? (y/n): ").strip().lower() == 'y':
            add_user_interactive()
            
    elif choice == "2":
        list_existing_users()
        
    elif choice == "3":
        print("Goodbye!")
        return
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
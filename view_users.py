#!/usr/bin/env python3
"""
Script to view all users in the Task Tracker application
Note: Passwords are encrypted and cannot be displayed for security reasons
"""

from app import app, db
from models import User
from datetime import datetime

def view_all_users():
    """Display all users in a formatted table"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in the database.")
            return
        
        print("\n" + "=" * 100)
        print("TASK TRACKER - ALL USERS")
        print("=" * 100)
        print(f"{'ID':<4} {'Name':<25} {'Username':<15} {'Email':<30} {'Role':<10} {'Department':<15} {'Status':<8}")
        print("-" * 100)
        
        for user in users:
            status = "Active" if user.is_active else "Inactive"
            department = user.department or "N/A"
            
            print(f"{user.id:<4} {user.full_name:<25} {user.username:<15} {user.email:<30} "
                  f"{user.role.title():<10} {department:<15} {status:<8}")
        
        print("-" * 100)
        print(f"Total users: {len(users)}")
        
        # Count by role
        managers = len([u for u in users if u.role == 'manager'])
        employees = len([u for u in users if u.role == 'employee'])
        print(f"Managers: {managers}, Employees: {employees}")
        
        # Count by status
        active = len([u for u in users if u.is_active])
        inactive = len([u for u in users if not u.is_active])
        print(f"Active: {active}, Inactive: {inactive}")

def reset_user_password():
    """Reset a user's password"""
    with app.app_context():
        print("\n" + "=" * 50)
        print("RESET USER PASSWORD")
        print("=" * 50)
        
        # List users first
        users = User.query.all()
        if not users:
            print("No users found.")
            return
            
        print("\nAvailable users:")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user.full_name} ({user.username})")
        
        try:
            choice = int(input(f"\nSelect user (1-{len(users)}): ")) - 1
            if 0 <= choice < len(users):
                selected_user = users[choice]
                new_password = input("Enter new password (min 6 characters): ").strip()
                
                if len(new_password) < 6:
                    print("❌ Password must be at least 6 characters!")
                    return
                
                selected_user.set_password(new_password)
                db.session.commit()
                
                print(f"✅ Password updated for {selected_user.full_name}")
                print(f"   Username: {selected_user.username}")
                print(f"   New password: {new_password}")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"❌ Error updating password: {str(e)}")
            db.session.rollback()

def main():
    print("Task Tracker User Management")
    print("=" * 30)
    print("1. View all users")
    print("2. Reset user password")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        view_all_users()
        
    elif choice == "2":
        reset_user_password()
        
    elif choice == "3":
        print("Goodbye!")
        return
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
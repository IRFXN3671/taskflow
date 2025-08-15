#!/usr/bin/env python3
"""
Bulk user creation script for Task Tracker
Creates multiple users at once from a predefined list
"""

from app import app, db
from models import User

# Define users to create
USERS_TO_CREATE = [
    {
        'username': 'nidaluser',
        'email': 'nidal@gmail.com',
        'first_name': 'Nidal',
        'last_name': 'CMP',
        'role': 'employee',
        'department': 'Management',
        'password': 'password123'
    },
    {
        'username': 'saninuser',
        'email': 'sanin@gmail.com',
        'first_name': 'Sanin',
        'last_name': 'Aboobacker',
        'role': 'employee',
        'department': 'testing',
        'password': 'password123'
    },
    {
        'username': 'mihaluser',
        'email': 'mihal@gmail.com',
        'first_name': 'Mihal',
        'last_name': 'Palakkal',
        'role': 'employee',
        'department': 'Deployment',
        'password': 'password123''
    },
    {
        'username': 'wasimuser',
        'email': 'wasim@gmail.ocm',
        'first_name': 'Wasim',
        'last_name': 'Sulthan',
        'role': 'employee',
        'department': 'QA',
        'password': 'password123'
    }
]

def create_bulk_users():
    """Create multiple users from the predefined list"""
    with app.app_context():
        print("Task Tracker - Bulk User Creation")
        print("=" * 40)
        
        created_users = []
        skipped_users = []
        
        for user_data in USERS_TO_CREATE:
            # Check if user already exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            existing_email = User.query.filter_by(email=user_data['email']).first()
            
            if existing_user or existing_email:
                skipped_users.append(user_data['username'])
                print(f"⚠️  Skipping '{user_data['username']}' - already exists")
                continue
            
            try:
                # Create new user
                new_user = User()
                new_user.username = user_data['username']
                new_user.email = user_data['email']
                new_user.first_name = user_data['first_name']
                new_user.last_name = user_data['last_name']
                new_user.role = user_data['role']
                new_user.department = user_data['department']
                new_user.set_password(user_data['password'])
                
                db.session.add(new_user)
                created_users.append(user_data)
                print(f"✅ Created '{user_data['username']}' ({user_data['role']})")
                
            except Exception as e:
                print(f"❌ Error creating '{user_data['username']}': {str(e)}")
                db.session.rollback()
                continue
        
        # Commit all changes
        if created_users:
            try:
                db.session.commit()
                print(f"\n🎉 Successfully created {len(created_users)} users!")
            except Exception as e:
                print(f"❌ Error committing changes: {str(e)}")
                db.session.rollback()
                return
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if created_users:
            print(f"✅ Created {len(created_users)} users:")
            for user in created_users:
                print(f"   • {user['first_name']} {user['last_name']} ({user['username']}) - {user['role'].title()}")
        
        if skipped_users:
            print(f"\n⚠️  Skipped {len(skipped_users)} existing users:")
            for username in skipped_users:
                print(f"   • {username}")
        
        # Print login credentials
        if created_users:
            print(f"\n🔐 LOGIN CREDENTIALS:")
            for user in created_users:
                print(f"   Username: {user['username']}")
                print(f"   Password: {user['password']}")
                print(f"   Role: {user['role'].title()}")
                print()

if __name__ == "__main__":
    create_bulk_users()
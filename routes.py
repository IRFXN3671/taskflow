from flask import render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, case
from app import app, db
from models import User, Task, Team, TeamMember

# Session management helpers
def login_user(user):
    session['user_id'] = user.id
    session['user_role'] = user.role

def logout_user():
    session.pop('user_id', None)
    session.pop('user_role', None)

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def manager_required(f):
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.is_manager():
            flash('Manager access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Authentication routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    
    # Get dashboard statistics
    if user.is_manager():
        # Manager dashboard stats
        total_tasks = Task.query.count()
        pending_tasks = Task.query.filter_by(status='pending').count()
        in_progress_tasks = Task.query.filter_by(status='in_progress').count()
        completed_tasks = Task.query.filter_by(status='completed').count()
        overdue_tasks = Task.query.filter(
            and_(Task.due_date < datetime.utcnow(), Task.status != 'completed')
        ).count()
        
        # Team performance data
        team_stats = db.session.query(
            User.first_name,
            User.last_name,
            func.count(Task.id).label('total_tasks'),
            func.sum(case((Task.status == 'completed', 1), else_=0)).label('completed_tasks')
        ).join(Task, User.id == Task.assignee_id).group_by(User.id, User.first_name, User.last_name).all()
        
        # Recent tasks
        recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
        
    else:
        # Employee dashboard stats
        total_tasks = user.assigned_tasks.count()
        pending_tasks = user.assigned_tasks.filter_by(status='pending').count()
        in_progress_tasks = user.assigned_tasks.filter_by(status='in_progress').count()
        completed_tasks = user.assigned_tasks.filter_by(status='completed').count()
        overdue_tasks = user.assigned_tasks.filter(
            and_(Task.due_date < datetime.utcnow(), Task.status != 'completed')
        ).count()
        
        team_stats = []
        recent_tasks = user.assigned_tasks.order_by(Task.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         user=user,
                         total_tasks=total_tasks,
                         pending_tasks=pending_tasks,
                         in_progress_tasks=in_progress_tasks,
                         completed_tasks=completed_tasks,
                         overdue_tasks=overdue_tasks,
                         team_stats=team_stats,
                         recent_tasks=recent_tasks)

# Task management routes
@app.route('/tasks')
@login_required
def tasks():
    user = get_current_user()
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    assignee_filter = request.args.get('assignee', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    
    # Build query based on user role
    if user.is_manager():
        query = Task.query
    else:
        query = user.assigned_tasks
    
    # Apply filters
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)
    
    if assignee_filter and user.is_manager():
        query = query.filter(Task.assignee_id == assignee_filter)
    
    if search_query:
        query = query.filter(
            or_(
                Task.title.contains(search_query),
                Task.description.contains(search_query),
                Task.tags.contains(search_query)
            )
        )
    
    # Apply sorting
    if sort_by == 'title':
        order_column = Task.title
    elif sort_by == 'due_date':
        order_column = Task.due_date
    elif sort_by == 'priority':
        order_column = Task.priority
    elif sort_by == 'status':
        order_column = Task.status
    else:
        order_column = Task.created_at
    
    if sort_order == 'asc':
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())
    
    tasks_list = query.all()
    
    # Get all employees for assignee filter (managers only)
    employees = []
    if user.is_manager():
        employees = User.query.filter_by(is_active=True).all()
    
    return render_template('tasks.html',
                         user=user,
                         tasks=tasks_list,
                         employees=employees,
                         current_filters={
                             'status': status_filter,
                             'priority': priority_filter,
                             'assignee': assignee_filter,
                             'search': search_query,
                             'sort': sort_by,
                             'order': sort_order
                         })

@app.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    user = get_current_user()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        assignee_id = request.form.get('assignee_id')
        priority = request.form.get('priority', 'medium')
        due_date_str = request.form.get('due_date')
        category = request.form.get('category')
        tags = request.form.get('tags')
        estimated_hours = request.form.get('estimated_hours')
        
        # Validate required fields
        if not title or not assignee_id:
            flash('Title and assignee are required.', 'danger')
            return redirect(url_for('create_task'))
        
        # Parse due date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format.', 'danger')
                return redirect(url_for('create_task'))
        
        # Parse estimated hours
        estimated_hours_float = None
        if estimated_hours:
            try:
                estimated_hours_float = float(estimated_hours)
            except ValueError:
                pass
        
        # Create new task
        task = Task(
            title=title,
            description=description,
            assignee_id=assignee_id,
            created_by_id=user.id,
            priority=priority,
            due_date=due_date,
            category=category,
            tags=tags,
            estimated_hours=estimated_hours_float
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks'))
    
    # Get employees for assignment dropdown
    employees = User.query.filter_by(is_active=True).all()
    
    return render_template('create_task.html', user=user, employees=employees)

@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    user = get_current_user()
    task = Task.query.get_or_404(task_id)
    
    # Check permissions
    if not user.is_manager() and task.assignee_id != user.id and task.created_by_id != user.id:
        flash('You do not have permission to edit this task.', 'danger')
        return redirect(url_for('tasks'))
    
    if request.method == 'POST':
        task.title = request.form.get('title', task.title)
        task.description = request.form.get('description', task.description)
        task.status = request.form.get('status', task.status)
        task.priority = request.form.get('priority', task.priority)
        task.category = request.form.get('category', task.category)
        task.tags = request.form.get('tags', task.tags)
        
        # Handle assignee change (managers only)
        if user.is_manager():
            assignee_id = request.form.get('assignee_id')
            if assignee_id:
                task.assignee_id = assignee_id
        
        # Handle due date
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid due date format.', 'warning')
        
        # Handle estimated and actual hours
        estimated_hours = request.form.get('estimated_hours')
        if estimated_hours:
            try:
                task.estimated_hours = float(estimated_hours)
            except ValueError:
                pass
        
        actual_hours = request.form.get('actual_hours')
        if actual_hours:
            try:
                task.actual_hours = float(actual_hours)
            except ValueError:
                pass
        
        # Update completed_at timestamp
        if task.status == 'completed' and not task.completed_at:
            task.completed_at = datetime.utcnow()
        elif task.status != 'completed':
            task.completed_at = None
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks'))
    
    # Get employees for assignment dropdown
    employees = User.query.filter_by(is_active=True).all()
    
    return render_template('edit_task.html', user=user, task=task, employees=employees)

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    user = get_current_user()
    task = Task.query.get_or_404(task_id)
    
    # Check permissions (only managers or task creator can delete)
    if not user.is_manager() and task.created_by_id != user.id:
        flash('You do not have permission to delete this task.', 'danger')
        return redirect(url_for('tasks'))
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks'))

# Analytics routes
@app.route('/analytics')
@login_required
@manager_required
def analytics():
    user = get_current_user()
    
    # Task completion analytics
    completion_data = db.session.query(
        func.date(Task.completed_at).label('date'),
        func.count(Task.id).label('completed_count')
    ).filter(
        Task.status == 'completed',
        Task.completed_at >= datetime.utcnow() - timedelta(days=30)
    ).group_by(func.date(Task.completed_at)).all()
    
    # Priority distribution
    priority_data = db.session.query(
        Task.priority,
        func.count(Task.id).label('count')
    ).group_by(Task.priority).all()
    
    # Status distribution
    status_data = db.session.query(
        Task.status,
        func.count(Task.id).label('count')
    ).group_by(Task.status).all()
    
    # Employee productivity
    productivity_data = db.session.query(
        User.first_name,
        User.last_name,
        func.count(Task.id).label('total_tasks'),
        func.sum(func.case((Task.status == 'completed', 1), else_=0)).label('completed_tasks'),
        func.avg(
            func.case(
                (Task.completed_at.isnot(None), 
                 func.extract('epoch', Task.completed_at - Task.created_at) / 3600),
                else_=None
            )
        ).label('avg_completion_time')
    ).join(Task, User.id == Task.assignee_id).group_by(User.id).all()
    
    return render_template('analytics.html',
                         user=user,
                         completion_data=completion_data,
                         priority_data=priority_data,
                         status_data=status_data,
                         productivity_data=productivity_data)

# API endpoints for real-time updates
@app.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    user = get_current_user()
    
    if user.is_manager():
        total_tasks = Task.query.count()
        pending_tasks = Task.query.filter_by(status='pending').count()
        in_progress_tasks = Task.query.filter_by(status='in_progress').count()
        completed_tasks = Task.query.filter_by(status='completed').count()
        overdue_tasks = Task.query.filter(
            and_(Task.due_date < datetime.utcnow(), Task.status != 'completed')
        ).count()
    else:
        total_tasks = user.assigned_tasks.count()
        pending_tasks = user.assigned_tasks.filter_by(status='pending').count()
        in_progress_tasks = user.assigned_tasks.filter_by(status='in_progress').count()
        completed_tasks = user.assigned_tasks.filter_by(status='completed').count()
        overdue_tasks = user.assigned_tasks.filter(
            and_(Task.due_date < datetime.utcnow(), Task.status != 'completed')
        ).count()
    
    return jsonify({
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'overdue_tasks': overdue_tasks
    })

# Admin routes for user management
@app.route('/admin/users')
@login_required
@manager_required
def admin_users():
    user = get_current_user()
    all_users = User.query.all()
    return render_template('admin_users.html', user=user, all_users=all_users)

@app.route('/admin/add-user', methods=['POST'])
@login_required
@manager_required
def admin_add_user():
    try:
        # Check if username or email already exists
        if User.query.filter_by(username=request.form.get('username')).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('admin_users'))
            
        if User.query.filter_by(email=request.form.get('email')).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('admin_users'))
        
        new_user = User()
        new_user.first_name = request.form.get('first_name')
        new_user.last_name = request.form.get('last_name')
        new_user.username = request.form.get('username')
        new_user.email = request.form.get('email')
        new_user.role = request.form.get('role')
        new_user.department = request.form.get('department')
        new_user.set_password(request.form.get('password'))
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'User {new_user.full_name} added successfully!', 'success')
    except Exception as e:
        flash('Error creating user. Please try again.', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin_users'))

@app.route('/admin/toggle-user/<int:user_id>', methods=['POST'])
@login_required
@manager_required
def admin_toggle_user(user_id):
    try:
        user_to_toggle = User.query.get(user_id)
        if user_to_toggle:
            user_to_toggle.is_active = not user_to_toggle.is_active
            db.session.commit()
            return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
    
    return jsonify({'success': False})

@app.route('/admin/reset-password/<int:user_id>', methods=['POST'])
@login_required
@manager_required
def admin_reset_password(user_id):
    try:
        user_to_reset = User.query.get(user_id)
        if user_to_reset:
            new_password = request.form.get('new_password')
            if len(new_password) >= 6:
                user_to_reset.set_password(new_password)
                db.session.commit()
                flash(f'Password updated for {user_to_reset.full_name}', 'success')
            else:
                flash('Password must be at least 6 characters', 'danger')
        else:
            flash('User not found', 'danger')
    except Exception as e:
        flash('Error updating password', 'danger')
        db.session.rollback()
    
    return redirect(url_for('admin_users'))

# Initialize demo data
@app.route('/init-demo-data')
def init_demo_data():
    """Initialize demo data for testing - remove in production"""
    
    # Create demo users
    if User.query.count() == 0:
        # Create manager
        manager = User(
            username='manager',
            email='manager@company.com',
            role='manager',
            first_name='John',
            last_name='Manager',
            department='Management'
        )
        manager.set_password('password123')
        
        # Create employees
        employee1 = User(
            username='employee1',
            email='employee1@company.com',
            role='employee',
            first_name='Alice',
            last_name='Smith',
            department='Development'
        )
        employee1.set_password('password123')
        
        employee2 = User(
            username='employee2',
            email='employee2@company.com',
            role='employee',
            first_name='Bob',
            last_name='Johnson',
            department='Development'
        )
        employee2.set_password('password123')
        
        db.session.add_all([manager, employee1, employee2])
        db.session.commit()
        
        flash('Demo users created! Login with: manager/password123 or employee1/password123', 'success')
    
    return redirect(url_for('login'))

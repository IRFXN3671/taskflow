# Task Tracker

## Overview

A Flask-based task management application that allows organizations to track and manage tasks with role-based access control. The system supports both managers and employees, where managers can create and assign tasks while employees can view and update their assigned tasks. The application provides comprehensive analytics, dashboard views, and real-time updates for effective project management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM for database operations
- **Database Models**: User and Task entities with role-based relationships
- **Authentication**: Session-based authentication with password hashing using Werkzeug
- **Authorization**: Role-based access control with decorators for manager-only features
- **Database**: SQLAlchemy with configurable database backend (environment-driven)

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap dark theme
- **UI Framework**: Bootstrap 5 with Feather icons for consistent design
- **JavaScript**: Vanilla JavaScript for dashboard auto-refresh and task management
- **Styling**: Custom CSS with dark theme support and responsive design

### Data Models
- **User Model**: Handles authentication, roles (manager/employee), and profile information
- **Task Model**: Manages task lifecycle with status tracking, priority levels, and assignment
- **Relationships**: Foreign key relationships between users and tasks for assignment and creation tracking

### Session Management
- Environment-based session secrets for security
- Custom decorators for login requirements and role-based access
- Helper functions for user authentication state management

### API Structure
- RESTful routes for task CRUD operations
- Dashboard statistics endpoint for real-time updates
- Form-based interactions with server-side validation
- JSON responses for AJAX functionality

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and application server
- **SQLAlchemy**: Database ORM and query builder
- **Werkzeug**: Password hashing and WSGI utilities
- **Jinja2**: Template rendering engine

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme support
- **Chart.js**: Data visualization for analytics dashboard
- **Feather Icons**: Icon library for consistent UI elements

### Database
- **Configurable Database**: Uses DATABASE_URL environment variable (supports PostgreSQL, SQLite, etc.)
- **Connection Pooling**: Configured with pool recycling and pre-ping for reliability

### Environment Configuration
- **SESSION_SECRET**: Session encryption and security
- **DATABASE_URL**: Database connection string
- **Debug Mode**: Development environment configuration
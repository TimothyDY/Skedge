# Skedge - Academic Schedule Management System

Skedge is a web-based academic schedule management system built with Flask that helps students organize their class schedules and academic events. It features a user-friendly interface with a modern design and supports both light and dark themes.

## Features

### User Management
- **Authentication System**
  - Secure login and registration
  - Role-based access (Admin/Student)
  - Password hashing for security
- **Profile Management**
  - Complete academic profile setup
  - Grade level selection (10-12)
  - Stream selection (Science/Social Studies)
  - Language selection (French, German, Japanese, Korean, Mandarin)
  - Class number assignment (1-10)
  - Subject selection based on stream

### Calendar System
- **Interactive Calendar Interface**
  - Monthly view with easy navigation
  - Real-time clock display
  - Day-by-day event organization
- **Event Management**
  - Add/delete events
  - Subject-based event creation
  - Custom time slots
  - Color-coding for better organization
  - Event details and descriptions
  - Persistent storage across sessions
- **Admin Features**
  - View student schedules
  - Access to all student profiles
  - Student data monitoring

### UI/UX Features
- **Responsive Design**
  - Works on desktop and mobile devices
  - Bootstrap 5.3.0 framework
  - Modern and clean interface
- **Theme Support**
  - Dark/Light mode toggle
  - Persistent theme preference
  - Consistent styling across pages
- **User-Friendly Navigation**
  - Intuitive menu structure
  - Quick access to important features
  - Clear visual feedback

## Technical Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: Flask-SQLAlchemy 3.1.1
- **Environment**: python-dotenv 1.0.0
- **Security**: Werkzeug 3.0.1
- **ORM**: SQLAlchemy 2.0.23
- **Template Engine**: Jinja2 3.1.2

### Frontend
- **Framework**: Bootstrap 5.3.0
- **Icons**: Bootstrap Icons 1.7.2
- **JavaScript**: Vanilla JS (ES6+)
- **CSS**: Custom styling with CSS3
- **HTML**: HTML5 with Jinja2 templating

## Project Structure
```
Skedge/
├── instance/
│   └── skedge.db
├── static/
│   └── assets/
│       └── SkedgeLogo.png
├── templates/
│   ├── admin.html
│   ├── calendar.html
│   ├── data_profile.html
│   ├── data_students.html
│   ├── index.html
│   ├── login.html
│   └── register.html
├── app.py
├── models.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/TimothyDY/Skedge.git
cd Skedge
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv env
env/Scripts/activate

# Linux/MacOS
python3 -m venv env
source env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Default Admin Account
- Username: admin
- Password: admin123

## Usage Guide

### For Students
1. Register a new account
2. Complete your academic profile:
   - Set your grade level (10-12)
   - Choose your stream (Science/Social Studies)
   - Select your language (French, German, Japanese, Korean, Mandarin)
   - Set your class number (1-10)
   - Select your subjects based on stream
3. Use the calendar to manage your schedule:
   - Click on any day to add an event
   - Select subject and time
   - Add event details
   - Choose custom colors
   - View and manage your events

### For Administrators
1. Login with admin credentials
2. Access the admin dashboard to:
   - View all student profiles
   - Access individual student schedules
   - Monitor student data

## Security Features
- Password hashing using Werkzeug
- Session-based authentication
- Role-based access control
- SQL injection protection via SQLAlchemy

## Browser Support
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Dependencies
All dependencies are listed in `requirements.txt` with their specific versions:
- Flask==3.0.0
- Flask-SQLAlchemy==3.1.1
- python-dotenv==1.0.0
- Werkzeug==3.0.1

Note: Other required packages will be automatically installed as dependencies of the above packages.
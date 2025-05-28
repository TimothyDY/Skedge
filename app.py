from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Profile, Event
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Get the absolute path of the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Ensure instance folder exists
instance_dir = os.path.join(base_dir, 'instance')
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)

# Set the database path to be in the instance folder
db_path = os.path.join(instance_dir, 'skedge.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def init_db():
    try:
        with app.app_context():
            # Drop all tables first to ensure a clean slate
            db.drop_all()
            print("Dropped all existing tables")
            
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    password=generate_password_hash('qwerty'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully")
            else:
                print("Admin user already exists")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise  # Re-raise the exception to see the full error

# Initialize database
init_db()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
        
    if user.role == 'admin':
        return redirect('/admin')

    # Force show profile if requested via query parameter
    force_profile = request.args.get('edit', 'false').lower() == 'true'
    if force_profile:
        return render_template('index.html', user=user)

    # Check if profile exists
    if not user.profile:
        return render_template('index.html', user=user)
        
    # Check if all required fields are filled
    profile = user.profile
    if not all([
        profile.full_name,
        profile.grade,
        profile.stream,
        profile.class_number,
        profile.language,
        profile.subjects
    ]):
        return render_template('index.html', user=user)
        
    return redirect('/calendar')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"Login attempt for username: {username}")
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            print(f"Login successful for {username}, role: {user.role}")
            session['user_id'] = user.id
            return redirect('/')
        
        print(f"Login failed for {username}")
        return render_template('login.html', error='Invalid username or password')
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
            
        user = User(
            username=username,
            password=generate_password_hash(password),
            role='student'
        )
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        return redirect('/')
        
    return render_template('register.html')

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        return redirect('/')
    
    students = User.query.filter_by(role='student').all()
    return render_template('admin.html', students=students)

@app.route('/calendar')
def calendar():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
    
    # If no profile or incomplete profile, redirect to profile page
    if not user.profile:
        return redirect('/')
        
    profile = user.profile
    if not all([
        profile.full_name,
        profile.grade,
        profile.stream,
        profile.class_number,
        profile.language,
        profile.subjects
    ]):
        return redirect('/')
    
    print(f"Loading calendar for user {user.id} ({user.username})")
    return render_template('calendar.html', user=user, is_admin_view=False)

@app.route('/calendar/<int:student_id>')
def view_student_calendar(student_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    current_user = User.query.get(session['user_id'])
    if not current_user or current_user.role != 'admin':
        return redirect('/')
        
    student = User.query.get(student_id)
    if not student:
        return "Student not found", 404
    
    print(f"Admin {current_user.id} viewing calendar for student {student.id}")
    return render_template('calendar.html', user=student, is_admin_view=True)

@app.route('/profile', methods=['POST'])
def create_profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
    
    profile = Profile(
        user_id=user.id,
        full_name=request.form['full_name'],
        grade=int(request.form['grade']),
        stream=request.form['stream'],
        class_number=int(request.form['class_number']),
        language=request.form['language'],
        subjects=','.join(request.form.getlist('subjects'))
    )
    
    db.session.add(profile)
    db.session.commit()
    
    return redirect('/calendar')

@app.route('/profile/<int:user_id>')
def view_profile(user_id):
    if 'user_id' not in session:
        return redirect('/login')
        
    current_user = User.query.get(session['user_id'])
    if not current_user:
        return redirect('/login')
        
    if current_user.role != 'admin' and current_user.id != user_id:
        return redirect('/')
        
    user = User.query.get(user_id)
    if not user:
        return "User not found", 404
    return render_template('data_profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user or not user.profile:
        return redirect('/')
    
    profile = user.profile
    profile.full_name = request.form['full_name']
    profile.grade = int(request.form['grade'])
    profile.stream = request.form['stream']
    profile.class_number = int(request.form['class_number'])
    profile.language = request.form['language']
    profile.subjects = ','.join(request.form.getlist('subjects'))
    
    db.session.commit()
    
    return redirect('/calendar')

@app.route('/data_students')
def data_students():
    if 'user_id' not in session:
        return redirect('/login')
        
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        return redirect('/')
    
    students = User.query.filter_by(role='student').all()
    return render_template("data_students.html", students=students)

@app.route('/data_customer')
def data_customer():
    users = User.query.all()
    users_tanpa_admin = User.query.filter_by(role='student').all()
    return render_template("data_customer.html", users = users, users_tanpa_admin = users_tanpa_admin)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

def create_admin():
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Creating admin account...")
            new_admin = User(
                username='admin',
                password=generate_password_hash('qwerty'),
                role='admin'
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Admin account created successfully!")
        else:
            print("Admin account exists, resetting password...")
            admin.password = generate_password_hash('qwerty')
            db.session.commit()
            print("Admin password reset successfully!")
    except Exception as e:
        print(f"Error managing admin account: {str(e)}")
        db.session.rollback()

# New routes for calendar events
@app.route('/api/events')
def get_events():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    current_user = User.query.get(session['user_id'])
    if not current_user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    # Get target user (either current user or student being viewed by admin)
    target_user_id = request.args.get('user_id', type=int)
    if target_user_id and current_user.role == 'admin':
        target_user = User.query.get(target_user_id)
        if not target_user:
            return jsonify({'error': 'Target user not found'}), 404
    else:
        target_user = current_user
    
    # Get month and year from query parameters
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    if month is None or year is None:
        return jsonify({'error': 'Month and year are required'}), 400
    
    try:
        print(f"Loading events for user {target_user.id}, month {month}, year {year}")
        # Query events for the specified month
        events = Event.query.filter(
            Event.user_id == target_user.id,
            db.extract('month', Event.date) == month,
            db.extract('year', Event.date) == year
        ).all()
        
        print(f"Found {len(events)} events")
        events_data = {}
        for event in events:
            date_key = event.date.strftime('%Y-%m-%d')
            if date_key not in events_data:
                events_data[date_key] = []
                
            events_data[date_key].append({
                'id': event.id,
                'subject': event.subject,
                'details': event.details,
                'startTime': event.start_time.strftime('%H:%M'),
                'endTime': event.end_time.strftime('%H:%M'),
                'color': event.color
            })
        
        return jsonify(events_data)
    except Exception as e:
        print(f"Error loading events: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/events', methods=['POST'])
def create_event():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    current_user = User.query.get(session['user_id'])
    if not current_user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    # Get target user (either current user or student being modified by admin)
    target_user_id = request.json.get('user_id')
    if target_user_id and current_user.role == 'admin':
        target_user = User.query.get(target_user_id)
        if not target_user:
            return jsonify({'error': 'Target user not found'}), 404
    else:
        target_user = current_user
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        print(f"Creating event for user {target_user.id}")
        event_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['startTime'], '%H:%M').time()
        end_time = datetime.strptime(data['endTime'], '%H:%M').time()
        
        event = Event(
            user_id=target_user.id,
            subject=data['subject'],
            details=data.get('details', ''),
            date=event_date,
            start_time=start_time,
            end_time=end_time,
            color=data.get('color', '#0d6efd')
        )
        
        db.session.add(event)
        db.session.commit()
        print(f"Event created with ID {event.id}")
        
        return jsonify({
            'id': event.id,
            'subject': event.subject,
            'details': event.details,
            'startTime': event.start_time.strftime('%H:%M'),
            'endTime': event.end_time.strftime('%H:%M'),
            'color': event.color
        })
        
    except (KeyError, ValueError) as e:
        print(f"Error creating event: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error creating event: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    current_user = User.query.get(session['user_id'])
    if not current_user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Allow admin to delete any event, but students can only delete their own
    if current_user.role != 'admin' and event.user_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully'})
    except Exception as e:
        print(f"Error deleting event: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)

import sqlite3
import hashlib
from datetime import datetime

def init_db():
    """Initialize the SQLite database with tables."""
    conn = sqlite3.connect('student_ai.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        age INTEGER,
        gender TEXT,
        address TEXT,
        attendance REAL DEFAULT 0,
        study_hours REAL DEFAULT 0,
        previous_gpa REAL DEFAULT 0,
        assignments_completed REAL DEFAULT 0,
        parent_income REAL DEFAULT 0,
        dropout_prediction INTEGER,
        dropout_probability REAL,
        predicted_gpa REAL,
        risk_level TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Add new columns if missing (migration) - ignore errors if exist
    try:
        c.execute("ALTER TABLE students ADD COLUMN health_issues REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE students ADD COLUMN sleep_hours REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE students ADD COLUMN extracurriculars REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE students ADD COLUMN mental_health_score REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    # Predictions history table
    c.execute('''CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        age INTEGER,
        attendance REAL,
        study_hours REAL,
        previous_gpa REAL,
        assignments_completed REAL,
        parent_income REAL,
        dropout_prediction INTEGER,
        dropout_probability REAL,
        predicted_gpa REAL,
        risk_level TEXT,
        predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )''')
    
    # Add prediction table new columns if missing - ignore errors if exist
    try:
        c.execute("ALTER TABLE predictions ADD COLUMN health_issues REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE predictions ADD COLUMN sleep_hours REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE predictions ADD COLUMN extracurriculars REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE predictions ADD COLUMN mental_health_score REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    # Admin user (default: admin/vsu2024)
    admin_password = hashlib.sha256('vsu2024'.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                  ('admin', 'admin@vsu.edu', admin_password, 'admin'))
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect('student_ai.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash."""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

def add_student(student_data):
    """Add a new student to the database."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''INSERT INTO students (
        student_id, first_name, last_name, email, phone, age, gender, address,
        attendance, study_hours, previous_gpa, assignments_completed, parent_income,
        health_issues, sleep_hours, extracurriculars, mental_health_score,
        dropout_prediction, dropout_probability, predicted_gpa, risk_level
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        student_data['student_id'],
        student_data['first_name'],
        student_data['last_name'],
        student_data.get('email', ''),
        student_data.get('phone', ''),
        student_data.get('age', 18),
        student_data.get('gender', ''),
        student_data.get('address', ''),
        student_data.get('attendance', 0),
        student_data.get('study_hours', 0),
        student_data.get('previous_gpa', 0),
        student_data.get('assignments_completed', 0),
        student_data.get('parent_income', 0),
        student_data.get('health_issues', 0),
        student_data.get('sleep_hours', 0),
        student_data.get('extracurriculars', 0),
        student_data.get('mental_health_score', 0),
        student_data.get('dropout_prediction', 0),
        student_data.get('dropout_probability', 0),
        student_data.get('predicted_gpa', 0),
        student_data.get('risk_level', 'Low')
    ))
    
    conn.commit()
    student_id = c.lastrowid
    conn.close()
    return student_id

def get_all_students():
    """Get all students from database."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students ORDER BY created_at DESC")
    students = c.fetchall()
    conn.close()
    return students

def get_student_by_id(student_id):
    """Get a specific student by student_id."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = c.fetchone()
    conn.close()
    return student

def update_student(student_id, student_data):
    """Update student information."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''UPDATE students SET
        first_name = ?, last_name = ?, email = ?, phone = ?, age = ?,
        gender = ?, address = ?, attendance = ?, study_hours = ?,
        previous_gpa = ?, assignments_completed = ?, parent_income = ?,
        dropout_prediction = ?, dropout_probability = ?, predicted_gpa = ?,
        risk_level = ?, updated_at = CURRENT_TIMESTAMP
    WHERE student_id = ?''', (
        student_data['first_name'],
        student_data['last_name'],
        student_data.get('email', ''),
        student_data.get('phone', ''),
        student_data.get('age', 18),
        student_data.get('gender', ''),
        student_data.get('address', ''),
        student_data.get('attendance', 0),
        student_data.get('study_hours', 0),
        student_data.get('previous_gpa', 0),
        student_data.get('assignments_completed', 0),
        student_data.get('parent_income', 0),
        student_data.get('dropout_prediction', 0),
        student_data.get('dropout_probability', 0),
        student_data.get('predicted_gpa', 0),
        student_data.get('risk_level', 'Low'),
        student_id
    ))
    
    conn.commit()
    conn.close()

def delete_student(student_id):
    """Delete a student from database."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()

def get_statistics():
    """Get overall statistics."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Total students
    c.execute("SELECT COUNT(*) as total FROM students")
    total_students = c.fetchone()['total']
    
    # At risk students (high dropout probability)
    c.execute("SELECT COUNT(*) as at_risk FROM students WHERE risk_level = 'High'")
    at_risk = c.fetchone()['at_risk']
    
    # Average GPA
    c.execute("SELECT AVG(predicted_gpa) as avg_gpa FROM students WHERE predicted_gpa > 0")
    avg_gpa = c.fetchone()['avg_gpa'] or 0
    
    # Average attendance
    c.execute("SELECT AVG(attendance) as avg_attendance FROM students")
    avg_attendance = c.fetchone()['avg_attendance'] or 0
    
    # Risk distribution
    c.execute("SELECT risk_level, COUNT(*) as count FROM students GROUP BY risk_level")
    risk_distribution = c.fetchall()
    
    conn.close()
    
    return {
        'total_students': total_students,
        'at_risk': at_risk,
        'avg_gpa': round(avg_gpa, 2),
        'avg_attendance': round(avg_attendance, 2),
        'risk_distribution': [dict(row) for row in risk_distribution]
    }

def save_prediction(student_id, prediction_data):
    """Save prediction to history."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''INSERT INTO predictions (
        student_id, age, attendance, study_hours, previous_gpa,
        assignments_completed, parent_income, dropout_prediction,
        dropout_probability, predicted_gpa, risk_level
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        student_id,
        prediction_data['age'],
        prediction_data['attendance'],
        prediction_data['study_hours'],
        prediction_data['previous_gpa'],
        prediction_data['assignments_completed'],
        prediction_data['parent_income'],
        prediction_data['dropout_prediction'],
        prediction_data['dropout_probability'],
        prediction_data['predicted_gpa'],
        prediction_data['risk_level']
    ))
    
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    """Authenticate user and return user data if valid."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and verify_password(password, user['password_hash']):
        return dict(user)
    return None

def register_user(username, email, password):
    """Register a new user."""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
                  (username, email, hash_password(password), 'user'))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

if __name__ == "__main__":
    init_db()

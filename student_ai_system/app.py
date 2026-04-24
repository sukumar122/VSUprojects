from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import joblib
import numpy as np
import pandas as pd
import io
import csv
from datetime import datetime
import os
from werkzeug.utils import secure_filename

import database
import auth
from auth import login_required, admin_required, get_current_user

app = Flask(__name__)
app.secret_key = 'vsu_college_secret_key_2024'

# Load ML models
try:
    dropout_model = joblib.load("dropout_model.pkl")
    gpa_model = joblib.load("gpa_model.pkl")
    scaler = joblib.load("scaler.pkl")
    models_loaded = True
except:
    models_loaded = False
    print("Warning: ML models not found. Run model_training.py first.")

# Initialize database on startup
database.init_db()

# ============ AUTH ROUTES ============

@app.route("/")
def index():
    """Landing page."""
    if auth.is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = database.authenticate_user(username, password)
        if user:
            auth.login_user(user['id'], user['username'], user['role'])
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    """Registration page."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if database.register_user(username, email, password):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username or email already exists.', 'error')
    
    return render_template('register.html')

@app.route("/logout")
def logout():
    """Logout route."""
    auth.logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# ============ DASHBOARD ROUTES ============

@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard page."""
    user = get_current_user()
    stats = database.get_statistics()
    
    # Get recent students
    conn = database.get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM students ORDER BY created_at DESC LIMIT 5")
    recent_students = c.fetchall()
    conn.close()
    
    return render_template('dashboard.html', 
                         user=user, 
                         stats=stats, 
                         recent_students=recent_students)

# ============ STUDENT MANAGEMENT ROUTES ============

@app.route("/students")
@login_required
def students():
    """List all students."""
    user = get_current_user()
    all_students = database.get_all_students()
    return render_template('students.html', students=all_students, user=user)

@app.route("/add_student", methods=['GET', 'POST'])
@login_required
def add_student():
    """Add new student page."""
    user = get_current_user()
    
    if request.method == 'POST':
        # Generate student ID
        student_id = f"STU{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get form data
        student_data = {
            'student_id': student_id,
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'age': int(request.form.get('age', 18)),
            'gender': request.form.get('gender'),
            'address': request.form.get('address'),
            'attendance': float(request.form.get('attendance', 0)),
            'study_hours': float(request.form.get('study_hours', 0)),
            'previous_gpa': float(request.form.get('previous_gpa', 0)),
            'assignments_completed': float(request.form.get('assignments_completed', 0)),
'parent_income': float(request.form.get('parent_income', 0)),
            'health_issues': float(request.form.get('health_issues', 3)),
            'sleep_hours': float(request.form.get('sleep_hours', 6)),
            'extracurriculars': float(request.form.get('extracurriculars', 4)),
            'mental_health_score': float(request.form.get('mental_health_score', 7)),
        }
        
        # Make prediction if models are loaded
        if models_loaded:
            prediction = make_prediction(student_data)
            student_data['dropout_prediction'] = prediction['dropout_prediction']
            student_data['dropout_probability'] = prediction['dropout_probability']
            student_data['predicted_gpa'] = prediction['predicted_gpa']
            student_data['risk_level'] = prediction['risk_level']
        
        database.add_student(student_data)
        flash(f'Student added successfully! ID: {student_id}', 'success')
        return redirect(url_for('students'))
    
    return render_template('add_student.html', user=user)

@app.route("/edit_student/<student_id>", methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """Edit student page."""
    user = get_current_user()
    student = database.get_student_by_id(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('students'))
    
    if request.method == 'POST':
        student_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'age': int(request.form.get('age', 18)),
            'gender': request.form.get('gender'),
            'address': request.form.get('address'),
            'attendance': float(request.form.get('attendance', 0)),
            'study_hours': float(request.form.get('study_hours', 0)),
            'previous_gpa': float(request.form.get('previous_gpa', 0)),
            'assignments_completed': float(request.form.get('assignments_completed', 0)),
'parent_income': float(request.form.get('parent_income', 0)),
            'health_issues': float(request.form.get('health_issues', 3)),
            'sleep_hours': float(request.form.get('sleep_hours', 6)),
            'extracurriculars': float(request.form.get('extracurriculars', 4)),
            'mental_health_score': float(request.form.get('mental_health_score', 7)),
        }
        
        # Make prediction if models are loaded
        if models_loaded:
            prediction = make_prediction(student_data)
            student_data['dropout_prediction'] = prediction['dropout_prediction']
            student_data['dropout_probability'] = prediction['dropout_probability']
            student_data['predicted_gpa'] = prediction['predicted_gpa']
            student_data['risk_level'] = prediction['risk_level']
        
        database.update_student(student_id, student_data)
        flash('Student updated successfully!', 'success')
        return redirect(url_for('students'))
    
    return render_template('edit_student.html', student=student, user=user)

@app.route("/delete_student/<student_id>")
@login_required
def delete_student(student_id):
    """Delete student route."""
    database.delete_student(student_id)
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students'))

@app.route("/add_all", methods=['GET', 'POST'])
@login_required
def add_all():
    """Bulk add students from CSV upload."""
    user = get_current_user()
    
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file selected.', 'error')
            return render_template('add_all.html', user=user)
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return render_template('add_all.html', user=user)
        
        try:
            # Read CSV
            df = pd.read_csv(file)
            
            added_count = 0
            skipped_count = 0
            
            for idx, row in df.iterrows():
                # Generate ID and names (since CSV has no names)
                student_id = f"BULK{datetime.now().strftime('%Y%m%d%H%M%S')}{idx:03d}"
                first_name = f"Student_{idx+1:03d}"
                last_name = "Bulk"
                
                # Map CSV columns to student_data (use provided or default)
                student_data = {
                    'student_id': student_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'age': int(row.get('age', 18)),
                    'attendance': float(row.get('attendance', 75)),
                    'study_hours': float(row.get('study_hours', 10)),
                    'previous_gpa': float(row.get('previous_gpa', 2.5)),
                    'assignments_completed': float(row.get('assignments_completed', 70)),
                    'parent_income': float(row.get('parent_income', 40000)),
                    'health_issues': float(row.get('health_issues', 3)),
                    'sleep_hours': float(row.get('sleep_hours', 6)),
                    'extracurriculars': float(row.get('extracurriculars', 4)),
                    'mental_health_score': float(row.get('mental_health_score', 7)),
                }
                
                # Skip if ID exists
                existing = database.get_student_by_id(student_id)
                if existing:
                    skipped_count += 1
                    continue
                
                # Generate prediction
                if models_loaded:
                    prediction = make_prediction(student_data)
                    student_data.update({
                        'dropout_prediction': prediction['dropout_prediction'],
                        'dropout_probability': prediction['dropout_probability'],
                        'predicted_gpa': prediction['predicted_gpa'],
                        'risk_level': prediction['risk_level']
                    })
                
                database.add_student(student_data)
                added_count += 1
            
            flash(f'Bulk import complete! Added {added_count} students, skipped {skipped_count} duplicates.', 'success')
            return redirect(url_for('students'))
        
        except Exception as e:
            flash(f'Error processing CSV: {str(e)}', 'error')
    
    return render_template('add_all.html', user=user)


# ============ PREDICTION ROUTES ============

@app.route("/predict", methods=['GET', 'POST'])
@login_required
def predict():
    """Prediction page."""
    user = get_current_user()
    prediction_result = None
    
    if request.method == 'POST':
        student_data = {
            'age': int(request.form.get('age', 20)),
            'attendance': float(request.form.get('attendance', 70)),
            'study_hours': float(request.form.get('study_hours', 5)),
            'previous_gpa': float(request.form.get('previous_gpa', 2.5)),
            'assignments_completed': float(request.form.get('assignments_completed', 60)),
            'parent_income': float(request.form.get('parent_income', 30000)),
            'health_issues': float(request.form.get('health_issues', 3)),
            'sleep_hours': float(request.form.get('sleep_hours', 6)),
            'extracurriculars': float(request.form.get('extracurriculars', 4)),
            'mental_health_score': float(request.form.get('mental_health_score', 7)),
        }
        
        if models_loaded:
            prediction_result = make_prediction(student_data)
            
            # Save prediction to history
            student_id = request.form.get('student_id')
            if student_id:
                database.save_prediction(student_id, {**student_data, **prediction_result})
        else:
            flash('ML models not loaded. Please run model_training.py first.', 'error')
    
    return render_template('predict.html', user=user, prediction=prediction_result)

@app.route("/api/predict", methods=["POST"])
@login_required
def api_predict():
    """API endpoint for predictions."""
    if not models_loaded:
        return jsonify({"error": "ML models not loaded"}), 500
    
    data = request.json
    student_data = {
        'age': data.get('age', 20),
        'attendance': data.get('attendance', 70),
        'study_hours': data.get('study_hours', 5),
        'previous_gpa': data.get('previous_gpa', 2.5),
        'assignments_completed': data.get('assignments_completed', 60),
        'parent_income': data.get('parent_income', 30000),
        'health_issues': data.get('health_issues', 3),
        'sleep_hours': data.get('sleep_hours', 6),
        'extracurriculars': data.get('extracurriculars', 4),
        'mental_health_score': data.get('mental_health_score', 7),
    }
    
    result = make_prediction(student_data)
    return jsonify(result)

# ============ ANALYTICS ROUTES ============

@app.route("/prediction_history")
@login_required
def prediction_history():
    """Prediction history page."""
    user = get_current_user()
    conn = database.get_db_connection()
    c = conn.cursor()
    
    # All predictions
    c.execute("""
        SELECT * FROM predictions 
        ORDER BY predicted_at DESC 
        LIMIT 1000
    """)
    predictions = c.fetchall()
    
    # Prediction stats
    c.execute("SELECT COUNT(*) as total FROM predictions")
    total_predictions = c.fetchone()['total']
    
    c.execute("SELECT AVG(predicted_gpa) as avg_gpa FROM predictions WHERE predicted_gpa > 0")
    avg_gpa = c.fetchone()['avg_gpa'] or 0
    
    c.execute("SELECT AVG(dropout_probability) * 100 as avg_dropout_prob FROM predictions")
    avg_dropout_prob = c.fetchone()['avg_dropout_prob'] or 0
    
    # Risk distribution
    c.execute("SELECT risk_level, COUNT(*) as count FROM predictions GROUP BY risk_level")
    risk_distribution = c.fetchall()
    
    # GPA distribution
    c.execute("""
        SELECT 
            CASE 
                WHEN predicted_gpa >= 3.5 THEN 'Excellent (3.5+)'
                WHEN predicted_gpa >= 3.0 THEN 'Good (3.0-3.49)'
                WHEN predicted_gpa >= 2.5 THEN 'Average (2.5-2.99)'
                WHEN predicted_gpa >= 2.0 THEN 'Below Average (2.0-2.49)'
                ELSE 'At Risk (<2.0)'
            END as gpa_range,
            COUNT(*) as count
        FROM predictions 
        WHERE predicted_gpa > 0
        GROUP BY gpa_range
    """)
    gpa_distribution = c.fetchall()
    
    conn.close()
    
    stats = {
        'total_predictions': total_predictions,
        'avg_gpa': round(float(avg_gpa), 2),
        'avg_dropout_prob': round(float(avg_dropout_prob), 1),
        'risk_distribution': [dict(row) for row in risk_distribution]
    }
    
    return render_template('prediction_history.html', predictions=predictions, user=user, stats=stats, gpa_distribution=[dict(row) for row in gpa_distribution])

@app.route("/analytics")
@login_required
def analytics():
    """Analytics page."""
    user = get_current_user()
    stats = database.get_statistics()
    
    # Get all students for detailed analysis
    conn = database.get_db_connection()
    c = conn.cursor()
    
    # GPA distribution
    c.execute("""
        SELECT 
            CASE 
                WHEN predicted_gpa >= 3.5 THEN 'Excellent (3.5+)'
                WHEN predicted_gpa >= 3.0 THEN 'Good (3.0-3.49)'
                WHEN predicted_gpa >= 2.5 THEN 'Average (2.5-2.99)'
                WHEN predicted_gpa >= 2.0 THEN 'Below Average (2.0-2.49)'
                ELSE 'At Risk (<2.0)'
            END as gpa_range,
            COUNT(*) as count
        FROM students 
        WHERE predicted_gpa > 0
        GROUP BY gpa_range
    """)
    gpa_distribution = c.fetchall()
    
    # Attendance analysis
    c.execute("""
        SELECT 
            CASE 
                WHEN attendance >= 90 THEN 'Excellent (90%+)'
                WHEN attendance >= 75 THEN 'Good (75-89%)'
                WHEN attendance >= 60 THEN 'Average (60-74%)'
                ELSE 'At Risk (<60%)'
            END as attendance_range,
            COUNT(*) as count
        FROM students 
        GROUP BY attendance_range
    """)
    attendance_distribution = c.fetchall()
    
    # Study hours analysis
    c.execute("""
        SELECT 
            CASE 
                WHEN study_hours >= 15 THEN 'High (15+ hrs)'
                WHEN study_hours >= 10 THEN 'Medium (10-14 hrs)'
                WHEN study_hours >= 5 THEN 'Low (5-9 hrs)'
                ELSE 'Minimal (<5 hrs)'
            END as study_range,
            COUNT(*) as count
        FROM students 
        GROUP BY study_range
    """)
    study_distribution = c.fetchall()
    
    conn.close()
    
    return render_template('analytics.html', 
                         user=user, 
                         stats=stats,
                         gpa_distribution=[dict(row) for row in gpa_distribution],
                         attendance_distribution=[dict(row) for row in attendance_distribution],
                         study_distribution=[dict(row) for row in study_distribution])

# ============ EXPORT ROUTES ============

@app.route("/export_csv")
@login_required
def export_csv():
    """Export student data to CSV."""
    students = database.get_all_students()
    
    # Create CSV in memory
    output = io.StringIO()
    if students:
        writer = csv.DictWriter(output, fieldnames=students[0].keys())
        writer.writeheader()
        for student in students:
            writer.writerow(dict(student))
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'students_export_{datetime.now().strftime("%Y%m%d")}.csv'
    )

# ============ HELPER FUNCTIONS ============

def make_prediction(student_data):
    """Make dropout and GPA prediction."""
    features = np.array([[
        student_data['age'],
        student_data['attendance'],
        student_data['study_hours'],
        student_data['previous_gpa'],
        student_data['assignments_completed'],
        student_data['parent_income'],
        student_data['health_issues'],
        student_data['sleep_hours'],
        student_data['extracurriculars'],
        student_data['mental_health_score']
    ]])
    
    features_scaled = scaler.transform(features)
    
    dropout_prediction = dropout_model.predict(features_scaled)[0]
    dropout_probability = dropout_model.predict_proba(features_scaled)[0][1]
    gpa_prediction = gpa_model.predict(features_scaled)[0]
    
    # Determine risk level
    risk_level = "Low"
    if dropout_probability > 0.7:
        risk_level = "High"
    elif dropout_probability > 0.4:
        risk_level = "Medium"
    
    return {
        "dropout_prediction": int(dropout_prediction),
        "dropout_probability": float(dropout_probability),
        "predicted_gpa": float(gpa_prediction),
        "risk_level": risk_level
    }

# ============ MAIN ============

if __name__ == "__main__":
    app.run(debug=True)

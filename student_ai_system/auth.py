from functools import wraps
from flask import session, redirect, url_for, flash
import database

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the currently logged in user."""
    if 'user_id' in session:
        conn = database.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = c.fetchone()
        conn.close()
        return dict(user) if user else None
    return None

def login_user(user_id, username, role):
    """Log in a user by setting session variables."""
    session['user_id'] = user_id
    session['username'] = username
    session['role'] = role
    session.permanent = True

def logout_user():
    """Log out the current user."""
    session.clear()

def is_logged_in():
    """Check if a user is logged in."""
    return 'user_id' in session

def is_admin():
    """Check if current user is admin."""
    return session.get('role') == 'admin'

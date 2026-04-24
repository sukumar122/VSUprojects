from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3, datetime, random, joblib, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

MODEL_PATH = "model/cyber_model.pkl"

# Initialize database
def init_db():
    conn = sqlite3.connect("behavior.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        role TEXT DEFAULT 'user',
        created_at TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS behavior(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        login_time TEXT,
        login_hour INTEGER,
        session_duration INTEGER,
        failed_attempts INTEGER,
        status TEXT,
        ip_address TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Load model
model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form["username"]
        p=request.form["password"]
        e=request.form.get("email", "")
        hashed_pw = generate_password_hash(p)
        try:
            conn=sqlite3.connect("behavior.db")
            conn.execute("INSERT INTO users(username,password,email,role,created_at) VALUES(?,?,?,?,?)",
                        (u, hashed_pw, e, 'user', str(datetime.datetime.now())))
            conn.commit()
            conn.close()
            flash("Registration successful! Please login.", "success")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("Username already exists", "danger")
            return redirect("/register")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    global model
    if request.method=="POST":
        u=request.form["username"]
        p=request.form["password"]
        conn=sqlite3.connect("behavior.db")
        cur=conn.cursor()
        cur.execute("SELECT id, username, password, role, email FROM users WHERE username=?", (u,))
        user=cur.fetchone()
        if user and check_password_hash(user[2], p):
            session["user"]=u
            session["user_id"]=user[0]
            session["role"]=user[3]
            session["email"]=user[4]
            
            login_hour=datetime.datetime.now().hour
            duration=random.randint(5,60)
            failed=random.randint(0,5)
            status="Normal"
            ip_address=request.remote_addr
            
            if model:
                pred=model.predict([[login_hour,duration,failed]])
                if pred[0]==-1:
                    status="Suspicious"
            
            conn.execute("INSERT INTO behavior(username,login_time,login_hour,session_duration,failed_attempts,status,ip_address) VALUES(?,?,?,?,?,?,?)",
                         (u,str(datetime.datetime.now()),login_hour,duration,failed,status,ip_address))
            conn.commit()
            conn.close()
            
            if user[3] == 'admin':
                return redirect("/admin")
            return redirect("/dashboard")
        else:
            flash("Invalid username or password", "danger")
            conn.close()
            return redirect("/login")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    conn=sqlite3.connect("behavior.db")
    cur=conn.cursor()
    cur.execute("SELECT login_time,login_hour,session_duration,failed_attempts,status FROM behavior WHERE username=?",(session["user"],))
    data=cur.fetchall()
    
    # Get statistics
    cur.execute("SELECT COUNT(*) FROM behavior WHERE username=?", (session["user"],))
    total_logins = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM behavior WHERE username=? AND status='Suspicious'", (session["user"],))
    suspicious_count = cur.fetchone()[0]
    
    conn.close()
    return render_template("dashboard.html",data=data,user=session["user"], 
                           total_logins=total_logins, suspicious_count=suspicious_count)

@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return "Access Denied", 403
    
    conn=sqlite3.connect("behavior.db")
    cur=conn.cursor()
    cur.execute("SELECT username,login_time,login_hour,session_duration,failed_attempts,status FROM behavior ORDER BY id DESC")
    data=cur.fetchall()
    
    # Get user statistics
    cur.execute("SELECT username, COUNT(*) as count FROM behavior GROUP BY username ORDER BY count DESC LIMIT 10")
    user_stats = cur.fetchall()
    
    # Get total users
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    # Get suspicious activities
    cur.execute("SELECT COUNT(*) FROM behavior WHERE status='Suspicious'")
    suspicious_total = cur.fetchone()[0]
    
    conn.close()
    return render_template("admin.html",data=data, user_stats=user_stats, 
                           total_users=total_users, suspicious_total=suspicious_total)

@app.route("/profile", methods=["GET","POST"])
def profile():
    if "user" not in session:
        return redirect("/login")
    
    conn=sqlite3.connect("behavior.db")
    cur=conn.cursor()
    
    if request.method=="POST":
        new_email = request.form.get("email", "")
        new_password = request.form.get("password", "")
        
        if new_password:
            hashed_pw = generate_password_hash(new_password)
            cur.execute("UPDATE users SET password=?, email=? WHERE username=?", 
                       (hashed_pw, new_email, session["user"]))
            flash("Password updated successfully!", "success")
        else:
            cur.execute("UPDATE users SET email=? WHERE username=?", 
                       (new_email, session["user"]))
            flash("Profile updated successfully!", "success")
        
        session["email"] = new_email
        conn.commit()
    
    cur.execute("SELECT username, email, role, created_at FROM users WHERE username=?", (session["user"],))
    user_data = cur.fetchone()
    conn.close()
    
    return render_template("profile.html", user_data=user_data)

@app.route("/predict", methods=["GET", "POST"])
def predict():
    result = None
    login_hour = None
    session_duration = None
    failed_attempts = None
    
    if request.method == "POST":
        login_hour = int(request.form.get("login_hour", 0))
        session_duration = int(request.form.get("session_duration", 0))
        failed_attempts = int(request.form.get("failed_attempts", 0))
        
        if model:
            pred = model.predict([[login_hour, session_duration, failed_attempts]])
            if pred[0] == -1:
                result = "Suspicious"
            else:
                result = "Normal"
        else:
            if login_hour < 6 or login_hour > 22 or failed_attempts > 3:
                result = "Suspicious"
            else:
                result = "Normal"
    
    return render_template("predict.html", result=result, 
                           login_hour=login_hour,
                           session_duration=session_duration,
                           failed_attempts=failed_attempts)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)

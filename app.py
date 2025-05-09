from flask import Flask, render_template, request, redirect, url_for, session
import secrets
import mysql.connector
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

def create_db_connection():
    try:
    # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",       # Replace with your MySQL host
            user="your_username",   # Replace with your MySQL username
            password="your_password",  # Replace with your MySQL password
            database="green_alert"  # Replace with your database name
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        else:
            print("Failed to connect to MySQL database")
            return None
    except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

def verify_user(email, password):
    try:
        connection = create_db_connection()
        if not connection:
            return None
        
        cursor = connection.cursor(dictionary=True)
        # Query to fetch user details
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            return user
        
        return None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get['email']
        password = request.form.get['password']
        
        if email or not password:
            return "Invalid credentials", 401
        
        try:
            admin = verify_user(email, password)
            if admin and admin['role'] == 'admin':
                session['user_type'] = 'admin'
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template('login_error.html')
        except Exception as e:
            return render_template('admin_login.html')
        
    return render_template('admin_login.html')

# Staff login route
@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Replace with actual staff authentication logic
        if username == 'staff' and password == 'staff123':
            session['user_type'] = 'staff'
            return redirect(url_for('staff_dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template('staff_login.html')

# Admin dashboard route
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

# Staff dashboard route
@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))
    return render_template('staff_dashboard.html')

# Manage users route
@app.route('/manage_users')
def manage_users():
    # Add logic to fetch and display users
    return render_template('manage_users.html')

# Manage alerts route
@app.route('/manage_alerts')
def manage_alerts():
    # Add logic to fetch and display alerts
    return render_template('manage_alerts.html')

# Reports route
@app.route('/reports')
def reports():
    # Add logic to fetch and display reports
    return render_template('reports.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
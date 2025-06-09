import token
from flask import Flask, render_template, request, redirect, url_for, session
import secrets
from flask_login import current_user, login_required, logout_user
from flask_mail import Mail, Message
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask import redirect, url_for, session

# Initialize Flask application
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

#for generating password rest tokens
s = URLSafeTimedSerializer(app.secret_key)

#Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_DEFAULT_SENDER'] = ''

mail = Mail(app)

# Database connection function
def create_db_connection():
    try:
    # Connect to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",       
             user="your_username",   
            password="your_password",
            database="green_alert"  
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
    
# Decorator to check user role
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('user_type') != role:
                return redirect(url_for('admin_login'))
            if session.get('user_type') != role:
                return redirect(url_for('staff_login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Home route
@app.route('/')
def index():
    return render_template('index.html')

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
        
        if not username or not password:
            return "Invalid credentials", 401
        
        staff = verify_user(username, password)
        if staff and staff['role'] == 'staff':
            session['user_type'] = 'staff'
            return redirect(url_for('staff_dashboard'))
        else:
            return render_template('login_error.html')
    return render_template('staff_login.html')

# Admin dashboard route
@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    #if session.get('user_type') != 'admin':
    #    return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

# Total staff
@app.route('/admin/dashboard/total_staff')
@login_required
@role_required('admin')
def total_staff_dash():
    return render_template('manage_staff.html')

# Register staff route
@app.route('/admin/dashboard/register_staff', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def register_staff():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        location = request.form.get('location')

        try:
            # Connect to the database
            connection = create_db_connection()
            if not connection:
                return "Database connection failed", 500

            cursor = connection.cursor()
            # Insert staff into the database
            query = """
                INSERT INTO staff (full_name, email, password, phone, location)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (full_name, email, generate_password_hash(password), phone, location))
            connection.commit()

            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard after successful registration
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return "An error occurred while registering", 500
        finally:
            if connection:
                connection.close()

    return render_template('register_staff.html')

# Register user route
@app.route('/staff/register', methods=['GET', 'POST'])
@login_required
@role_required('staff')
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        location = request.form.get('location')

        try:
            # Connect to the database
            connection = create_db_connection()
            if not connection:
                return "Database connection failed", 500

            cursor = connection.cursor()
            # Insert user into the database
            query = """
                INSERT INTO users (full_name, email, password, phone, location)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (full_name, email, phone, location))
            connection.commit()

            return redirect(url_for('regsuccess'))  # Redirect to login after successful registration
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return "An error occurred while registering", 500
        finally:
            if connection:
                connection.close()

    return render_template('register_user.html')

# Registration success route
@app.route('/regsuccess')
def regsuccess():
    return render_template('reg_success.html')

# Staff dashboard route
@app.route('/staff/dashboard')
@login_required
@role_required('staff')
def staff_dashboard():
    if session.get('user_type') != 'staff':
        return redirect(url_for('staff_login'))
    return render_template('staff_dashboard.html')

# Manage users route
@app.route('/admin/dashboard/manage_users')
@login_required
@role_required('admin')
def manage_users():
    # Add logic to fetch and display users
    return render_template('manage_users.html')

# Manage alerts route
@app.route('/admin/dashboard/manage_alerts')
@login_required
@role_required('admin')
def manage_alerts():
    # Add logic to fetch and display alerts
    return render_template('manage_alerts.html')

# Reports route
@app.route('/admin/dashboard/reports')
@login_required
@role_required('admin')
def reports():
    # Add logic to fetch and display reports
    return render_template('reports.html')

# Delete staff
@app.route('/delete_staff/<int:staff_id>')
@login_required
@role_required('admin')
def delete_staff(staff_id):
    try:
        connection = create_db_connection()
        cursor = connection.cursor()
        # Delete staff from the database
        query = "DELETE FROM users WHERE id = %s"
        cursor.execute(query, (staff_id,))
        connection.commit()
        return redirect(url_for('manage_users'))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "An error occurred while deleting staff", 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

            
# check if the user exists in the database before sending the reset link
def find_user_by_email(email):
    try:
        connection = create_db_connection()
        cursor = connection.cursor(dictionary=True)
        # Query to fetch user details
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        return user
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

# Forgot password route
@app.route('/forgot_password', methods=['GET', 'POST'])
@login_required
def forgot_password():
    source = request.args.get('source')

    if request.method == 'POST':
        email = request.form.get('email')
        user = find_user_by_email(email)
        if user:
            token = s.dumps(f'{email}|{source}', salt='password-reset-salt')
            link = url_for('reset_password', token=token, _external=True)
            
            msg = Message('Password Reset Request', recipients=[email])
            msg.body = f'Someone requested your password reset.If you did not request this ignor this message.\n Click the link to reset your password:\n {link}'
            mail.send(msg)

            return render_template('forgot_password_success.html')
        else:
            return render_template('forgot_password.html', error='Email not found')
    return render_template('forgot_password.html')

# Reset password route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        data = s.loads(token, salt='password-reset-salt', max_age=600)
        email, source = data.split('|')

    except (SignatureExpired, BadSignature, ValueError) as e:
            return render_template('reset_password.html', error='Invalid or expired token')
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or new_password != confirm_password:
            return redirect(url_for('reset_password', token=token))
        
        hashed_password = generate_password_hash(new_password)
        try:
            connection = create_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET password = %s WHERE email = %s",
                (hashed_password, email))
            connection.commit()
            return render_template('reset_password_success.html')
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return render_template('reset_password.html', error='An error occurred while updating the password')
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    return render_template('reset_password.html', token=token)

# Logout route
@app.route('/logout')
def logout():
    logout_user()
    session.pop('email', None)

    if current_user.is_authenticated:

        if current_user.role == 'admin':
            return redirect(url_for('admin_login'))
        else:
            return redirect(url_for('staff_login'))

if __name__ == '__main__':
    app.run(debug=True)

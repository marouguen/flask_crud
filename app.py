from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

app = Flask(__name__)
app.secret_key = "12011986"

# Database connection parameters
DB_HOST = "db"  # Use "localhost" if running locally
DB_NAME = "crud_app_db"
DB_USER = "postgres"
DB_PASS = "admin"

# Function to connect to the database
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
    )

# Function to initialize the database
def initialize_database():
    """Creates the required tables if they do not already exist."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Create users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    """)

    # Create students table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        name VARCHAR(150) NOT NULL,
        age INT NOT NULL
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully.")

# Route: Home Page (Read + Search Functionality)
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    query = request.args.get('query', '').strip()
    conn = get_db_connection()
    cur = conn.cursor()

    # Search for students by name or age
    if query:
        cur.execute("""
        SELECT * FROM students
        WHERE name ILIKE %s OR CAST(age AS TEXT) ILIKE %s;
        """, (f"%{query}%", f"%{query}%"))
    else:
        cur.execute("SELECT * FROM students;")
    
    students = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", students=students, query=query)

# Route: Add Student (Create Operation)
@app.route('/add', methods=('GET', 'POST'))
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO students (name, age) VALUES (%s, %s)", (name, age))
        conn.commit()
        cur.close()
        conn.close()
        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template("add.html")

# Route: Edit Student (Update Operation)
@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        cur.execute("UPDATE students SET name = %s, age = %s WHERE id = %s", (name, age, id))
        conn.commit()
        cur.close()
        conn.close()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))
    
    cur.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("edit.html", student=student)

# Route: Delete Student (Delete Operation)
@app.route('/delete/<int:id>', methods=('GET', 'POST'))
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        cur.execute("DELETE FROM students WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Student deleted successfully!', 'success')
        return redirect(url_for('index'))
    
    cur.execute("SELECT * FROM students WHERE id = %s", (id,))
    student = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("delete.html", student=student)

# Route: Register User
@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except psycopg2.errors.UniqueViolation:
            flash('Username already exists', 'error')
            conn.rollback()
        finally:
            cur.close()
            conn.close()
    return render_template('register.html')

# Route: Login User
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

# Route: Logout User
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Run the app
if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=True)

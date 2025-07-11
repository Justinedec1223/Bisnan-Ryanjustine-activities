from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
import os
from werkzeug.utils import secure_filename
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        db.close()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        db.close()
        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    search = request.args.get('search', '')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if search:
        cursor.execute("SELECT * FROM employees WHERE name LIKE %s", (f"%{search}%",))
    else:
        cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    db.close()
    return render_template('dashboard.html', employees=employees, search=search)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        file = request.files['photo']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO employees (name, position, photo) VALUES (%s, %s, %s)", (name, position, filename))
        db.commit()
        db.close()
        return redirect('/dashboard')
    return render_template('add_employee.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        file = request.files.get('photo')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            cursor.execute("UPDATE employees SET name=%s, position=%s, photo=%s WHERE id=%s", (name, position, filename, id))
        else:
            cursor.execute("UPDATE employees SET name=%s, position=%s WHERE id=%s", (name, position, id))
        db.commit()
        db.close()
        return redirect('/dashboard')
    cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
    employee = cursor.fetchone()
    db.close()
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete/<int:id>')
def delete_employee(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
    db.commit()
    db.close()
    return redirect('/dashboard')

if __name__ == "__main__":
    app.run(debug=True)

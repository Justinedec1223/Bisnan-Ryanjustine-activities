from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, password))
        db.commit()
        flash('Account created! You can now login.', 'success')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password_input):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully!', 'success')
            return redirect('/')
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'success')
    return redirect('/login')

@app.route('/employees')
def employees():
    if 'user_id' not in session:
        return redirect('/login')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    return render_template('employees.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO employees (name, email, position) VALUES (%s, %s, %s)",
                       (name, email, position))
        db.commit()
        flash('Employee added!', 'success')
        return redirect('/employees')
    return render_template('add_employee.html')

@app.route('/edit_employee/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    if 'user_id' not in session:
        return redirect('/login')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        cursor.execute("UPDATE employees SET name=%s, email=%s, position=%s WHERE id=%s",
                       (name, email, position, id))
        db.commit()
        flash('Employee updated!', 'success')
        return redirect('/employees')
    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    employee = cursor.fetchone()
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    if 'user_id' not in session:
        return redirect('/login')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
    db.commit()
    flash('Employee deleted.', 'danger')
    return redirect('/employees')

if __name__ == '__main__':
    app.run(debug=True)

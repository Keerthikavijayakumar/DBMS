from flask import Flask, render_template, request, redirect, url_for
from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from flask import session, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
def get_db_connection():
    conn = sqlite3.connect('it_company.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/charts-data')
def charts_data():
    conn = get_db_connection()

    # Employees per project
    emp_data = conn.execute('''
        SELECT p.name AS project_name, COUNT(e.id) AS employee_count
        FROM projects p
        LEFT JOIN employees e ON p.id = e.project_id
        GROUP BY p.id
    ''').fetchall()

    # Project status distribution
    status_data = conn.execute('''
        SELECT status, COUNT(*) AS count
        FROM projects
        GROUP BY status
    ''').fetchall()

    conn.close()

    return {
        "employee": {
            "labels": [row["project_name"] for row in emp_data],
            "counts": [row["employee_count"] for row in emp_data]
        },
        "status": {
            "labels": [row["status"] for row in status_data],
            "counts": [row["count"] for row in status_data]
        }
    }







@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin_user = request.form['username']
        admin_pass = request.form['password']
        if admin_user == 'admin' and admin_pass == 'admin123':
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('You need to be logged in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function




@app.route('/')
def dashboard():
    conn = get_db_connection()
    projects = conn.execute('''
        SELECT projects.*, clients.name as client_name, clients.company as client_company
        FROM projects
        LEFT JOIN clients ON projects.client_id = clients.id
    ''').fetchall()
    clients = conn.execute('SELECT * FROM clients').fetchall()
    employees = conn.execute('''
    SELECT employees.*, projects.name AS project_name
    FROM employees
    LEFT JOIN projects ON employees.project_id = projects.id
''').fetchall()

    conn.close()
    return render_template('dashboard.html', projects=projects, clients=clients, employees=employees)

# ===================== PROJECTS =====================@app.route('/add_project', methods=['GET', 'POST'])
 
@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        name = request.form['name']
        status = request.form['status']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        client_id = request.form['client_id']

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO projects (name, status, start_date, end_date, client_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, status, start_date, end_date, client_id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    clients = conn.execute('SELECT * FROM clients').fetchall()
    conn.close()
    return render_template('add_project.html', clients=clients)



@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    conn = sqlite3.connect('it_company.db')
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        status = request.form['status']
        client_id = request.form['client_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Update the project in the database
        cur.execute('''
            UPDATE projects
            SET name = ?, status = ?, client_id = ?, start_date = ?, end_date = ?
            WHERE id = ?
        ''', (name, status, client_id, start_date, end_date, project_id))

        conn.commit()
        conn.close()
        return redirect('/dashboard')

    # Get existing project details
    cur.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cur.fetchone()
    conn.close()

    return render_template('edit_project.html', project=project)

@app.route('/delete_project/<int:id>')
def delete_project(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM projects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# ===================== CLIENTS =====================
@app.route('/add_client', methods=['POST'])
def add_client():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    company = request.form['company']
    conn = get_db_connection()
    conn.execute('INSERT INTO clients (name, email, phone, address, company) VALUES (?, ?, ?, ?, ?)',
                 (name, email, phone, address, company))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/edit_client/<int:id>', methods=['GET', 'POST'])
def edit_client(id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        company = request.form['company']
        conn.execute('''
            UPDATE clients
            SET name = ?, email = ?, phone = ?, address = ?, company = ?
            WHERE id = ?
        ''', (name, email, phone, address, company, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    client = conn.execute('SELECT * FROM clients WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_client.html', client=client)

@app.route('/delete_client/<int:id>')
def delete_client(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM clients WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# ===================== EMPLOYEES =====================
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    conn = get_db_connection()
    if request.method == 'POST':
        try:
            name = request.form['name']
            role = request.form['role']
            email = request.form['email']
            phone = request.form['phone']
            department = request.form['department']
            project_id = request.form.get('project_id')
            project_id = int(project_id) if project_id else None

            conn.execute('''
                INSERT INTO employees (name, role, email, phone, department, project_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, role, email, phone, department, project_id))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))

        except Exception as e:
            conn.close()
            print("ERROR adding employee:", e)
            return "An error occurred while adding the employee. Check terminal."
    else:
        projects = conn.execute('SELECT id, name FROM projects').fetchall()
        conn.close()
        return render_template('add_employee.html', projects=projects)


@app.route('/edit_employee/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']
        conn.execute('''
            UPDATE employees
            SET name = ?, role = ?, email = ?, phone = ?, department = ?
            WHERE id = ?
        ''', (name, role, email, phone, department, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    employee = conn.execute('SELECT * FROM employees WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

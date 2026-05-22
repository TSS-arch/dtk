from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = '/home/testbyte/mysite/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# 🔹 CREATE DATABASE
# =========================
def init_db():

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    # =========================
    # REPORTS TABLE
    # =========================
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            location TEXT,
            description TEXT,
            image TEXT,
            solution TEXT DEFAULT ''
        )
    ''')

    # =========================
    # SERVICE PROFILES TABLE
    # =========================
    c.execute('''
        CREATE TABLE IF NOT EXISTS service_profiles (
            id TEXT PRIMARY KEY,
            name TEXT,
            mobile TEXT,
            occupation TEXT,
            address TEXT,
            photo TEXT,
            service_areas TEXT,
            center_lat REAL,
            center_lon REAL,
            radius_km INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # =========================
    # SUGGESTIONS TABLE
    # =========================
    c.execute('''
        CREATE TABLE IF NOT EXISTS suggestions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            mobile TEXT,

            category TEXT,

            suggestion TEXT

        )
    ''')

    # =========================
    # USERS TABLE
    # =========================
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            mobile TEXT,
            dob TEXT,
            blood TEXT,
            address TEXT,
            photo TEXT
        )
    ''')

    # =========================
    # JOB POSTS TABLE
    # =========================
    c.execute('''
        CREATE TABLE IF NOT EXISTS job_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            job_location TEXT NOT NULL,
            salary TEXT,
            job_type TEXT,
            job_description TEXT,
            posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')

    conn.commit()
    conn.close()

# AUTO CREATE TABLES
init_db()

# =========================
# 🔹 SUGGESTION PAGE
# =========================
@app.route("/suggestion")
def home():

    return render_template("suggestion.html")

# =========================
# 🔹 SUBMIT SUGGESTION
# =========================
@app.route("/submit_suggestion", methods=["POST"])
def submit_suggestion():

    try:

        data = request.get_json()

        name = data.get("name")
        mobile = data.get("mobile")
        category = data.get("category")
        suggestion = data.get("suggestion")

        # ✅ FIXED DATABASE
        conn = sqlite3.connect("reports.db")

        cursor = conn.cursor()

        cursor.execute("""

        INSERT INTO suggestions
        (name, mobile, category, suggestion)

        VALUES (?, ?, ?, ?)

        """, (name, mobile, category, suggestion))

        conn.commit()
        conn.close()

        return jsonify({
            "success": True
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

# =========================
# 🔹 HOME PAGE
# =========================
@app.route('/apps')
def index():
    return render_template('index.html')

@app.route('/')
def indexx():
    return render_template('indexx.html')


@app.route('/complaint')
def complaint():
    return render_template('complaint.html')

@app.route('/profile')
def pro():
    return render_template('profile.html')

@app.route('/health')
def health():
    return render_template('health.html')

@app.route('/women-help')
def indexs():
    return render_template('women.html')

@app.route('/education')
def edu():
    return render_template('education.html')

@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

# =========================
# 🔹 SEARCH
# =========================
@app.route('/find_service')
def find_service():

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    # Workers
    c.execute("SELECT * FROM service_profiles")
    results = c.fetchall()

    # Occupations
    c.execute("SELECT DISTINCT occupation FROM service_profiles")
    occupations = [x[0] for x in c.fetchall()]

    # Areas
    c.execute("SELECT DISTINCT service_areas FROM service_profiles")
    areas = [x[0] for x in c.fetchall()]

    # Jobs
    c.execute("""
        SELECT * FROM job_posts
        WHERE is_active = 1
        ORDER BY posted_date DESC
    """)

    job_posts = c.fetchall()

    conn.close()

    return render_template(
        'search.html',
        results=results,
        occupations=occupations,
        areas=areas,
        job_posts=job_posts
    )

# =========================
# 🔹 POST JOB
# =========================
@app.route('/post_job', methods=['POST'])
def post_job():

    try:

        job_title = request.form.get('job_title')
        company_name = request.form.get('company_name')
        contact_number = request.form.get('contact_number')
        job_location = request.form.get('job_location')
        salary = request.form.get('salary')
        job_type = request.form.get('job_type')
        job_description = request.form.get('job_description')

        if not all([
            job_title,
            company_name,
            contact_number,
            job_location
        ]):

            return jsonify({
                'success': False,
                'message': 'Please fill all required fields'
            })

        conn = sqlite3.connect('reports.db')
        c = conn.cursor()

        c.execute('''
            INSERT INTO job_posts
            (
                job_title,
                company_name,
                contact_number,
                job_location,
                salary,
                job_type,
                job_description
            )

            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_title,
            company_name,
            contact_number,
            job_location,
            salary,
            job_type,
            job_description
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Job posted successfully!'
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'message': str(e)
        })

# =========================
# 🔹 API JOBS
# =========================
@app.route('/api/jobs')
def api_get_jobs():

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    c.execute("""
        SELECT * FROM job_posts
        WHERE is_active = 1
        ORDER BY posted_date DESC
    """)

    jobs = c.fetchall()

    conn.close()

    return jsonify([{
        'id': j[0],
        'title': j[1],
        'company': j[2],
        'contact': j[3],
        'location': j[4],
        'salary': j[5],
        'job_type': j[6],
        'description': j[7],
        'date': j[8]
    } for j in jobs])

# =========================
# 🔹 DELETE JOB
# =========================
@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):

    try:

        conn = sqlite3.connect('reports.db')
        c = conn.cursor()

        c.execute("""
            UPDATE job_posts
            SET is_active = 0
            WHERE id = ?
        """, (job_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Job deleted successfully'
        })

    except Exception as e:

        return jsonify({
            'success': False,
            'message': str(e)
        })

# =========================
# 🔹 SUBMIT REPORT
# =========================
@app.route('/submit', methods=['POST'])
def submit():

    category = request.form['category']
    location = request.form['location']
    description = request.form['description']

    file = request.files['photo']

    filename = ""

    if file and file.filename != "":

        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )
        )

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    c.execute('''
        INSERT INTO reports
        (category, location, description, image)

        VALUES (?, ?, ?, ?)
    ''', (
        category,
        location,
        description,
        filename
    ))

    conn.commit()
    conn.close()

    return redirect(url_for('popup'))

# =========================
# 🔹 POPUP PAGE
# =========================
@app.route('/popup')
def popup():
    return render_template('popup.html')

# =========================
# 🔹 VIEW REPORTS
# =========================
@app.route('/reports')
def reports():

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    c.execute("SELECT * FROM reports")

    data = c.fetchall()

    conn.close()

    return render_template(
        'reports.html',
        reports=data
    )

# =========================
# 🔹 SERVICE PROFILE
# =========================
@app.route('/service_profile', methods=['GET', 'POST'])
def service_profile():

    if request.method == 'POST':

        name = request.form.get('name')
        mobile = request.form.get('mobile')
        occupation = request.form.get('occupation')
        address = request.form.get('address')

        service_areas = request.form.get('service_areas')

        try:

            center_lat = float(request.form.get('center_lat', 0))
            center_lon = float(request.form.get('center_lon', 0))
            radius_km = int(request.form.get('radius_km', 0))

        except:

            center_lat = 0
            center_lon = 0
            radius_km = 0

        file = request.files.get('photo')

        filename = ""

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

        conn = sqlite3.connect('reports.db')
        c = conn.cursor()

        user_id = str(uuid.uuid4())

        c.execute('''
            INSERT INTO service_profiles
            (
                id,
                name,
                mobile,
                occupation,
                address,
                photo,
                service_areas,
                center_lat,
                center_lon,
                radius_km
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            name,
            mobile,
            occupation,
            address,
            filename,
            service_areas,
            center_lat,
            center_lon,
            radius_km
        ))

        conn.commit()
        conn.close()

        return f"Saved Successfully! ID: {user_id}"

    return render_template('worker.html')

# =========================
# 🔹 ADMIN PANEL
# =========================
@app.route('/admin')
def admin():

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    # Reports
    c.execute("SELECT * FROM reports")
    reports = c.fetchall()

    # Users
    c.execute("SELECT * FROM users")
    users = c.fetchall()

    # Services
    c.execute("SELECT * FROM service_profiles")
    services = c.fetchall()

    # Job Posts
    c.execute("""
        SELECT * FROM job_posts
        ORDER BY posted_date DESC
    """)

    job_posts = c.fetchall()

    # Suggestions
    c.execute("""
        SELECT * FROM suggestions
        ORDER BY id DESC
    """)

    suggestions = c.fetchall()

    conn.close()

    return render_template(
        'admin.html',
        reports=reports,
        users=users,
        services=services,
        job_posts=job_posts,
        suggestions=suggestions
    )

# =========================
# 🔹 UPDATE SOLUTION
# =========================
@app.route('/update_solution', methods=['POST'])
def update_solution():

    report_id = request.form['id']
    solution = request.form['solution']

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    c.execute("""
        UPDATE reports
        SET solution=?
        WHERE id=?
    """, (
        solution,
        report_id
    ))

    conn.commit()
    conn.close()

    return redirect('/admin')

# =========================
# 🔹 SAVE USER PROFILE
# =========================
@app.route('/save_profile', methods=['POST'])
def save_profile():

    name = request.form['name']
    mobile = request.form['mobile']
    dob = request.form['dob']
    blo = request.form['blo']
    address = request.form['address']

    file = request.files['photo']

    filename = ""

    if file and file.filename != "":

        filename = secure_filename(file.filename)

        file.save(
            os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )
        )

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    user_id = str(uuid.uuid4())

    c.execute('''
        INSERT INTO users
        (
            id,
            name,
            mobile,
            dob,
            blood,
            address,
            photo
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        name,
        mobile,
        dob,
        blo,
        address,
        filename
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for(
            'id_card',
            user_id=user_id
        )
    )

# =========================
# 🔹 ID CARD
# =========================
@app.route('/id_card/<user_id>')
def id_card(user_id):

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    c.execute("""
        SELECT * FROM users
        WHERE id=?
    """, (user_id,))

    user = c.fetchone()

    conn.close()

    return render_template(
        'id_card.html',
        user=user
    )

# =========================
# 🔹 EMPLOYMENT HUB
# =========================
@app.route('/employment_hub')
def employment_hub():
    return render_template('employment_hub.html')

@app.route('/post_job_page')
def post_job_page():
    return render_template('post_job.html')

@app.route('/search_jobs_page')
def search_jobs_page():

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    c.execute("""
        SELECT * FROM job_posts
        WHERE is_active = 1
        ORDER BY posted_date DESC
    """)

    job_posts = c.fetchall()

    conn.close()

    return render_template(
        'search_jobs.html',
        job_posts=job_posts
    )

@app.route('/join_worker_page')
def join_worker_page():
    return render_template('join_worker.html')

@app.route('/search_worker_page')
def search_worker_page():

    conn = sqlite3.connect('reports.db')
    c = conn.cursor()

    c.execute("SELECT * FROM service_profiles")
    results = c.fetchall()

    c.execute("""
        SELECT DISTINCT occupation
        FROM service_profiles
        WHERE occupation IS NOT NULL
    """)

    occupations = [x[0] for x in c.fetchall()]

    conn.close()

    return render_template(
        'search_worker.html',
        results=results,
        occupations=occupations
    )

# =========================
# 🔹 RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)
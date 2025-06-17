from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory, current_app
import json, os
from werkzeug.utils import secure_filename
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

DATA_DIR = 'data'
GALLERY_DIR = 'static/gallery'
ADMIN_PASSWORD = 'adminaccess01x'

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), encoding="utf-8") as f:
        return json.load(f)
def save_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin.login'))
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Wrong password', 'error')
    return render_template('admin_login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Load
    courses = load_json('courses.json')
    gallery = load_json('gallery.json')
    team = load_json('team.json')
    blogs = load_json('blogs.json')
    achievements = load_json('achievements.json')
    if request.method == 'POST':
        action = request.form.get('action')
        # --- Courses ---
        if action == 'add_course':
            new = {
                "name": request.form['name'],
                "description": request.form['description'],
                "max_people": int(request.form['max_people']),
                "date": request.form['date'],
                "time": request.form['time'],
                "price": request.form['price']
            }
            courses.append(new)
            save_json('courses.json', courses)
            flash("Course added", "success")
        elif action == 'remove_course':
            idx = int(request.form['idx'])
            del courses[idx]
            save_json('courses.json', courses)
            flash("Course removed", "success")
        # --- Gallery ---
        elif action == 'add_gallery':
            file = request.files.get('photo')
            if file and allowed_file(file.filename):
                fname = secure_filename(file.filename)
                path = os.path.join(GALLERY_DIR, fname)
                file.save(path)
                gallery.append(fname)
                save_json('gallery.json', gallery)
                flash("Photo uploaded", "success")
            else:
                flash("Invalid file", "error")
        elif action == 'remove_gallery':
            fname = request.form['filename']
            if fname in gallery:
                gallery.remove(fname)
                save_json('gallery.json', gallery)
                try:
                    os.remove(os.path.join(GALLERY_DIR, fname))
                except Exception:
                    pass
                flash("Photo removed", "success")
        # --- Team ---
        elif action == 'add_team':
            member = {
                "name": request.form['name'],
                "role": request.form['role'],
                "bio": request.form['bio'],
                "photo": ""
            }
            file = request.files.get('photo')
            if file and allowed_file(file.filename):
                fname = secure_filename(file.filename)
                path = os.path.join('static/team', fname)
                file.save(path)
                member['photo'] = fname
            team.append(member)
            save_json('team.json', team)
            flash("Team member added", "success")
        elif action == 'remove_team':
            idx = int(request.form['idx'])
            del team[idx]
            save_json('team.json', team)
            flash("Team member removed", "success")
        # --- Blogs ---
        elif action == 'add_blog':
            blog = {
                "title": request.form['title'],
                "short_text": request.form['short_text'],
                "full_text": request.form['full_text'],
                "date": datetime.now().strftime('%Y-%m-%d'),
                "is_long": len(request.form['full_text']) > 200
            }
            blogs.insert(0, blog)  # newest first
            save_json('blogs.json', blogs)
            flash("Blog added", "success")
        elif action == 'remove_blog':
            idx = int(request.form['idx'])
            del blogs[idx]
            save_json('blogs.json', blogs)
            flash("Blog removed", "success")
        # --- Achievements ---
        elif action == 'add_achievement':
            achievements.append(request.form['achievement'])
            save_json('achievements.json', achievements)
            flash("Achievement added", "success")
        elif action == 'remove_achievement':
            idx = int(request.form['idx'])
            del achievements[idx]
            save_json('achievements.json', achievements)
            flash("Achievement removed", "success")
        return redirect(url_for('admin.dashboard'))
    return render_template('admin.html',
        courses=courses, gallery=gallery, team=team,
        blogs=blogs, achievements=achievements)

# To serve uploaded images
@admin_bp.route('/gallery/<filename>')
def gallery_file(filename):
    return send_from_directory(GALLERY_DIR, filename)

@admin_bp.route('/team/<filename>')
def team_file(filename):
    return send_from_directory('static/team', filename)

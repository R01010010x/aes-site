from flask import Flask, render_template, request, redirect, url_for, flash
app = Flask(__name__)

import os
import smtplib
from email.message import EmailMessage
from admin import admin_bp

app.secret_key = "your_secret_key_here"  # For Flash messages
app.register_blueprint(admin_bp)

BLOG_LIMIT = 10
ACHIEVEMENT_LIMIT = 10

def load_json(filename):
    with open(os.path.join('data', filename), encoding="utf-8") as f:
        return json.load(f)

@app.route('/')
def home():
    return render_template('home.html', active_page='home')

@app.route('/news/aktuelles')
def news():
    blogs = load_json('blogs.json')
    achievements = load_json('achievements.json')
    return render_template('news.html',
        blogs=blogs[:BLOG_LIMIT],
        achievements=achievements[:ACHIEVEMENT_LIMIT]
    )

@app.route('/news/archiv')
def archive():
    blogs = load_json('blogs.json')
    achievements = load_json('achievements.json')
    return render_template('archive.html',
        blogs=blogs[BLOG_LIMIT:],
        achievements=achievements[ACHIEVEMENT_LIMIT:]
    )

@app.route('/ueber-uns/team')
def team():
    team = load_json('team.json')
    return render_template('team.html', team=team)

@app.route('/ueber-uns/galerie')
def gallery():
    images = load_json('gallery.json')
    return render_template('gallery.html', images=images)

@app.route('/angebote/kurse')
def courses():
    courses = load_json('courses.json')
    return render_template('courses.html', courses=courses)

@app.route('/angebote/events')
def events():
    return render_template('events.html', active_page='offers')

@app.route('/kontakt', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form.get('email')
        message = request.form.get('message')
        if not email or not message:
            flash('Bitte alle Felder ausfüllen.', 'error')
            return redirect(url_for('contact'))
        try:
            send_email(email, message)
            flash('Deine Nachricht wurde gesendet!', 'success')
        except Exception as e:
            flash('Beim Senden ist ein Fehler aufgetreten. Bitte später erneut versuchen.', 'error')
        return redirect(url_for('contact'))
    return render_template('contact.html', active_page='contact')

def send_email(sender_email, message_content):
    # SMTP configuration
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USER = ''      # Mail
    SMTP_PASS = ''      # password / App password
    RECEIVER = 'arcumetscientiam@gmail.com'
    msg = EmailMessage()
    msg['Subject'] = 'Kontaktformular Website'
    msg['From'] = sender_email
    msg['To'] = RECEIVER
    msg.set_content(message_content)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)

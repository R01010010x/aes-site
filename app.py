from flask import Flask, render_template, request, redirect, url_for, flash
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for flashing messages

# --- Helper: Auto-populate gallery images ---
def get_gallery_images():
    gallery_path = os.path.join(app.static_folder, "images", "gallery")
    files = []
    if os.path.exists(gallery_path):
        for fname in os.listdir(gallery_path):
            if fname.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".svg")):
                files.append("images/gallery/" + fname)
    files.sort()
    return files

@app.route('/')
def home():
    return render_template('home.html', active_page='home')

@app.route('/news')
def news():
    return render_template('news.html', active_page='news')

@app.route('/archive')
def archive():
    return render_template('archive.html', active_page='news')

@app.route('/team')
def team():
    return render_template('team.html', active_page='about')

@app.route('/gallery')
def gallery():
    images = get_gallery_images()
    return render_template('gallery.html', images=images, active_page='about')

@app.route('/courses')
def courses():
    return render_template('courses.html', active_page='offers')

@app.route('/events')
def events():
    return render_template('events.html', active_page='offers')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form.get('email')
        message = request.form.get('message')
        if not email or not message:
            flash('All fields are required.', 'error')
            return redirect(url_for('contact'))
        try:
            send_email(email, message)
            flash('Your message has been sent!', 'success')
        except Exception as e:
            flash('There was an error sending your message. Please try again later.', 'error')
        return redirect(url_for('contact'))
    return render_template('contact.html', active_page='contact')

def send_email(sender_email, message_content):
    # ---- FILL IN WITH SMTP CREDENTIALS ----
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    SMTP_USER = ''      # email here
    SMTP_PASS = ''      # email password or app password here
    RECEIVER = 'arcumetscientiam@gmail.com'
    # ---------------------------------------
    msg = EmailMessage()
    msg['Subject'] = 'Website Contact Form'
    msg['From'] = sender_email
    msg['To'] = RECEIVER
    msg.set_content(message_content)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)

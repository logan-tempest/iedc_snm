from flask import Flask, render_template, request, flash, redirect, url_for
import smtplib
from email.mime.text import MIMEText  # Fixed: MIMEText not MimeText
from email.mime.multipart import MIMEMultipart  # Fixed: MIMEMultipart not MimeMultipart

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Important for flash messages

# Mock database for events (we'll replace with real DB later)
events = [
    {"id": 1, "title": "Startup Bootcamp", "date": "2024-02-15", "description": "Learn the basics of starting up"},
    {"id": 2, "title": "Hackathon 2024", "date": "2024-03-10", "description": "24-hour coding competition"},
    {"id": 3, "title": "Investor Meet", "date": "2024-04-05", "description": "Connect with potential investors"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        
        # Here you would typically save to database or send email
        # For now, we'll just show a success message
        flash(f'Thank you {name}! Your message has been sent. We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/events')
def events_list():
    return render_template('events.html', events=events)

@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, flash, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'iedc-snmimt-secret-key-2024'  # Change this to any random string

# Mock data for events
events = [
    {"id": 1, "title": "Startup Bootcamp", "date": "2024-02-15", "description": "Learn the basics of starting up", "location": "IEDC Lab"},
    {"id": 2, "title": "Hackathon 2024", "date": "2024-03-10", "description": "24-hour coding competition", "location": "Computer Lab"},
    {"id": 3, "title": "Investor Meet", "date": "2024-04-05", "description": "Connect with potential investors", "location": "Conference Hall"},
]

# File to store contact messages
MESSAGES_FILE = 'contact_messages.json'

def init_messages_file():
    """Create messages file if it doesn't exist"""
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w') as f:
            json.dump([], f)

def save_contact_message(name, email, subject, message):
    """Save contact form submissions to a JSON file"""
    try:
        # Create messages list or load existing
        try:
            with open(MESSAGES_FILE, 'r') as f:
                messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []
        
        # Add new message
        new_message = {
            'id': len(messages) + 1,
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'read': False
        }
        
        messages.append(new_message)
        
        # Save back to file
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
        
        print(f"✅ Message saved: {name} - {subject}")  # Debug print
        return True
    except Exception as e:
        print(f"❌ Save error: {e}")
        return False

def get_message_stats():
    """Get statistics about messages"""
    try:
        with open(MESSAGES_FILE, 'r') as f:
            messages = json.load(f)
        total = len(messages)
        unread = len([msg for msg in messages if not msg['read']])
        return total, unread
    except:
        return 0, 0

# Initialize messages file when app starts
init_messages_file()

@app.route('/')
def home():
    total_messages, unread_messages = get_message_stats()
    return render_template('index.html', 
                         total_messages=total_messages, 
                         unread_messages=unread_messages)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Basic validation
        if not name or not email or not subject or not message:
            flash('Please fill in all fields.', 'error')
            return redirect('/contact')
        
        # Save message to file
        if save_contact_message(name, email, subject, message):
            flash(f'Thank you {name}! Your message has been received. We will contact you soon.', 'success')
        else:
            flash('Sorry, there was an error saving your message. Please try again.', 'error')
        
        return redirect('/contact')
    
    return render_template('contact.html')

@app.route('/events')
def events_list():
    return render_template('events.html', events=events)

@app.route('/team')
def team():
    return render_template('team.html')

# Admin route to view messages (optional - for you to check messages)
@app.route('/admin/messages')
def view_messages():
    try:
        with open(MESSAGES_FILE, 'r') as f:
            messages = json.load(f)
        return render_template('message_list.html', messages=messages)
    except:
        return "No messages yet."

if __name__ == '__main__':
    app.run(debug=True)
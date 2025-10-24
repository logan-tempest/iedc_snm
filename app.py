from flask import Flask, render_template, request, flash, redirect, url_for, send_file
import json
import os
import pandas as pd
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'iedc-snmimt-secret-key-2024'

# Files for data storage
MESSAGES_FILE = 'contact_messages.json'
EVENTS_FILE = 'events_data.json'
REGISTRATIONS_FILE = 'event_registrations.json'

# Sample events data
sample_events = [
    {
        "id": 1, 
        "title": "Startup Bootcamp 2024", 
        "date": "2024-02-15", 
        "time": "10:00 AM - 4:00 PM",
        "description": "Learn the fundamentals of starting your own venture. Perfect for beginners!",
        "location": "IEDC Innovation Lab", 
        "seats": 50,
        "registered": 0,
        "image": "startup-bootcamp.jpg",
        "category": "Workshop",
        "status": "upcoming"
    },
    {
        "id": 2, 
        "title": "Hackathon 2024", 
        "date": "2024-03-10", 
        "time": "9:00 AM - Next Day 9:00 AM",
        "description": "24-hour coding competition. Build innovative solutions and win exciting prizes!",
        "location": "Computer Lab Block", 
        "seats": 100,
        "registered": 0,
        "image": "hackathon.jpg",
        "category": "Competition",
        "status": "upcoming"
    },
    {
        "id": 3, 
        "title": "Investor Connect Meet", 
        "date": "2024-04-05", 
        "time": "2:00 PM - 5:00 PM",
        "description": "Connect with angel investors and venture capitalists. Pitch your ideas!",
        "location": "College Conference Hall", 
        "seats": 30,
        "registered": 0,
        "image": "investor-meet.jpg",
        "category": "Networking",
        "status": "upcoming"
    }
]

def init_data_files():
    """Create data files if they don't exist"""
    # Contact messages
    if not os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'w') as f:
            json.dump([], f)
    
    # Events data
    if not os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'w') as f:
            json.dump(sample_events, f, indent=2)
    
    # Event registrations
    if not os.path.exists(REGISTRATIONS_FILE):
        with open(REGISTRATIONS_FILE, 'w') as f:
            json.dump([], f)

def save_contact_message(name, email, subject, message):
    """Save contact form submissions to JSON file"""
    try:
        with open(MESSAGES_FILE, 'r') as f:
            messages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        messages = []
    
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
    
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)
    
    return True

def get_events():
    """Get all events from file"""
    try:
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    except:
        return sample_events

def save_event_registration(event_id, name, email, phone, department, year, message):
    """Save event registration to file"""
    try:
        with open(REGISTRATIONS_FILE, 'r') as f:
            registrations = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        registrations = []
    
    # Get event details
    events = get_events()
    event = next((e for e in events if e['id'] == event_id), None)
    
    if not event:
        return False, "Event not found"
    
    # Check if seats available
    if event['registered'] >= event['seats']:
        return False, "Event is full"
    
    # Check if already registered
    existing_reg = next((r for r in registrations if r['email'] == email and r['event_id'] == event_id), None)
    if existing_reg:
        return False, "Already registered for this event"
    
    new_registration = {
        'id': len(registrations) + 1,
        'event_id': event_id,
        'event_title': event['title'],
        'name': name,
        'email': email,
        'phone': phone,
        'department': department,
        'year': year,
        'message': message,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'status': 'confirmed'
    }
    
    registrations.append(new_registration)
    
    # Update event registration count
    for e in events:
        if e['id'] == event_id:
            e['registered'] += 1
            break
    
    # Save both files
    with open(REGISTRATIONS_FILE, 'w') as f:
        json.dump(registrations, f, indent=2)
    
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)
    
    return True, "Registration successful"

def get_event_registrations(event_id=None):
    """Get all registrations, optionally filtered by event"""
    try:
        with open(REGISTRATIONS_FILE, 'r') as f:
            registrations = json.load(f)
        
        if event_id:
            return [r for r in registrations if r['event_id'] == event_id]
        return registrations
    except:
        return []

def export_registrations_to_excel(event_id=None):
    """Export registrations to Excel file"""
    registrations = get_event_registrations(event_id)
    
    if not registrations:
        return None, "No registrations found"
    
    # Create DataFrame
    df_data = []
    for reg in registrations:
        df_data.append({
            'Registration ID': reg['id'],
            'Event ID': reg['event_id'],
            'Event Title': reg['event_title'],
            'Name': reg['name'],
            'Email': reg['email'],
            'Phone': reg['phone'],
            'Department': reg['department'],
            'Year': reg['year'],
            'Message': reg['message'],
            'Registration Date': reg['timestamp'],
            'Status': reg['status']
        })
    
    df = pd.DataFrame(df_data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Registrations', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Registrations']
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output, "Excel file generated successfully"

# Initialize data files when app starts
init_data_files()

@app.route('/')
def home():
    events = get_events()
    upcoming_events = [e for e in events if e['status'] == 'upcoming'][:3]
    return render_template('index.html', upcoming_events=upcoming_events)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not name or not email or not subject or not message:
            flash('Please fill in all fields.', 'error')
            return redirect('/contact')
        
        if save_contact_message(name, email, subject, message):
            flash(f'Thank you {name}! Your message has been received.', 'success')
        else:
            flash('Sorry, there was an error. Please try again.', 'error')
        
        return redirect('/contact')
    
    return render_template('contact.html')

@app.route('/events')
def events_list():
    events = get_events()
    return render_template('events.html', events=events)

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    events = get_events()
    event = next((e for e in events if e['id'] == event_id), None)
    
    if not event:
        flash('Event not found.', 'error')
        return redirect('/events')
    
    # Get available seats
    available_seats = event['seats'] - event['registered']
    
    return render_template('event_detail.html', event=event, available_seats=available_seats)

@app.route('/event/<int:event_id>/register', methods=['GET', 'POST'])
def event_register(event_id):
    events = get_events()
    event = next((e for e in events if e['id'] == event_id), None)
    
    if not event:
        flash('Event not found.', 'error')
        return redirect('/events')
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        year = request.form.get('year', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validation
        if not all([name, email, phone, department, year]):
            flash('Please fill in all required fields.', 'error')
            return redirect(f'/event/{event_id}/register')
        
        success, result_message = save_event_registration(
            event_id, name, email, phone, department, year, message
        )
        
        if success:
            flash(f'Successfully registered for {event["title"]}!', 'success')
            return redirect('/events')
        else:
            flash(result_message, 'error')
            return redirect(f'/event/{event_id}/register')
    
    available_seats = event['seats'] - event['registered']
    return render_template('event_register.html', event=event, available_seats=available_seats)

@app.route('/team')
def team():
    return render_template('team.html')

# Admin routes
@app.route('/admin/messages')
def view_messages():
    try:
        with open(MESSAGES_FILE, 'r') as f:
            messages = json.load(f)
        return render_template('message_list.html', messages=messages)
    except:
        return "No messages yet."

@app.route('/admin/registrations')
def view_registrations():
    registrations = get_event_registrations()
    events = get_events()
    
    # Get statistics
    total_registrations = len(registrations)
    events_with_registrations = {}
    
    for event in events:
        event_regs = [r for r in registrations if r['event_id'] == event['id']]
        events_with_registrations[event['id']] = {
            'event': event,
            'count': len(event_regs)
        }
    
    return render_template('registration_list.html', 
                         registrations=registrations, 
                         events=events,
                         total_registrations=total_registrations,
                         events_with_registrations=events_with_registrations)

@app.route('/admin/export-registrations')
def export_all_registrations():
    """Export all registrations to Excel"""
    excel_file, message = export_registrations_to_excel()
    
    if excel_file:
        filename = f"IEDC_All_Registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        flash(message, 'error')
        return redirect('/admin/registrations')

@app.route('/admin/export-event-registrations/<int:event_id>')
def export_event_registrations(event_id):
    """Export registrations for a specific event to Excel"""
    events = get_events()
    event = next((e for e in events if e['id'] == event_id), None)
    
    if not event:
        flash('Event not found.', 'error')
        return redirect('/admin/registrations')
    
    excel_file, message = export_registrations_to_excel(event_id)
    
    if excel_file:
        filename = f"IEDC_{event['title'].replace(' ', '_')}_Registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            excel_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        flash(message, 'error')
        return redirect('/admin/registrations')

if __name__ == '__main__':
    app.run(debug=True)
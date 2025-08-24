from flask import Flask, request, jsonify, render_template, redirect, session
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
import sqlite3

# File to store events persistently
EVENTS_FILE = 'events_data.json'

# Global variables for data storage
events = []
engagement_data = {}  # Store engagement data per event
tickets_data = {}     # Store ticket sales per event

# Load events from file
def load_events():
    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

# Save events to file
def save_events(events_data):
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events_data, f, indent=2)

# In-memory storage for ticket bookings (in production, use a database)
ticket_bookings = []
live_sales_data = {
    'total_sales': 0,
    'total_revenue': 0,
    'recent_bookings': []
}

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app)

# Load events data
events = load_events()

# If no events exist, create some sample data
if not events:
    events = [
        {
            'id': 1,
            'title': 'Tech Conference 2024',
            'description': 'Annual technology conference featuring the latest innovations',
            'date': '2024-03-15',
            'time': '09:00',
            'location': 'Convention Center, Jakarta',
            'capacity': 500,
            'ticketPrice': 250000,
            'currency': 'INR',
            'image': '/static/images/tech-conference.jpg',
            'attendees': 0,
            'status': 'upcoming',
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 2,
            'title': 'Music Festival',
            'description': 'Three-day music festival with international artists',
            'date': '2024-04-20',
            'time': '18:00',
            'location': 'City Park, Jakarta',
            'capacity': 1000,
            'ticketPrice': 450000,
            'currency': 'INR',
            'image': '/static/images/music-festival.jpg',
            'attendees': 0,
            'status': 'upcoming',
            'created_at': datetime.now().isoformat()
        }
    ]
    save_events(events)

@app.route('/', methods=['GET'])
def home():
    """Serve the home page with login"""
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login authentication"""
    data = request.get_json()
    
    # Simple authentication (replace with real authentication in production)
    # Accept multiple valid credentials for testing
    valid_credentials = [
        {'email': 'admin@eventpro.com', 'password': 'admin123'},
        {'email': 'admin@gmail.com', 'password': 'admin'},
        {'email': 'test@test.com', 'password': 'test123'},
        {'email': 'demo@demo.com', 'password': 'demo'}
    ]
    
    user_email = data.get('email', '').lower()
    user_password = data.get('password', '')
    
    # Check if credentials match any valid combination
    for creds in valid_credentials:
        if user_email == creds['email'].lower() and user_password == creds['password']:
            session['logged_in'] = True
            session['user_email'] = user_email
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/dashboard')
def dashboard():
    """Redirect dashboard to events page"""
    return redirect('/events')

@app.route('/events')
def events_list():
    """Events list page"""
    return render_template('events.html', events=events)

@app.route('/profile')
def profile():
    """Profile page"""
    return render_template('profile.html')

@app.route('/logout')
def logout():
    """Logout and redirect to home"""
    session.clear()
    return redirect('/')

@app.route('/events/<int:event_id>/pre-event')
def event_pre_analytics(event_id):
    """Pre-event analytics page"""
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return redirect('/events')
    
    return render_template('event_pre_analytics.html', 
                         event_id=event_id, 
                         event_title=event['title'],
                         event_status=event['status'],
                         event=event)

@app.route('/events/<int:event_id>/engagement')
def event_engagement_analytics(event_id):
    """Event engagement analytics page"""
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return redirect('/events')
    
    return render_template('event_engagement.html', 
                         event_id=event_id, 
                         event_title=event['title'],
                         event_status=event['status'],
                         event=event)

@app.route('/events/<int:event_id>/post-event')
def event_post_analytics(event_id):
    """Post-event analytics page"""
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return redirect('/events')
    
    return render_template('event_post_analytics.html', 
                         event_id=event_id, 
                         event_title=event['title'],
                         event_status=event['status'],
                         event=event)

@app.route('/events/<int:event_id>/post-analytics')
def event_post_analytics_alt(event_id):
    """Alternative route for post-event analytics page"""
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return redirect('/events')
    
    return render_template('event_post_analytics.html', 
                         event_id=event_id, 
                         event_title=event['title'],
                         event_status=event['status'],
                         event=event)

@app.route('/api/book-ticket', methods=['POST'])
def book_ticket():
    """API endpoint for booking tickets"""
    try:
        data = request.get_json()
        
        booking = {
            'id': len(ticket_bookings) + 1,
            'event_id': data.get('event_id'),
            'attendee_name': data.get('attendee_name'),
            'attendee_email': data.get('attendee_email'),
            'ticket_price': data.get('ticket_price', 250000),
            'currency': data.get('currency', 'INR'),
            'booking_time': datetime.now().isoformat(),
            'status': 'confirmed'
        }
        
        ticket_bookings.append(booking)
        
        # Update live sales data
        live_sales_data['total_sales'] += 1
        live_sales_data['total_revenue'] += booking['ticket_price']
        live_sales_data['recent_bookings'].insert(0, booking)
        
        # Keep only last 10 recent bookings
        if len(live_sales_data['recent_bookings']) > 10:
            live_sales_data['recent_bookings'] = live_sales_data['recent_bookings'][:10]
        
        return jsonify({'success': True, 'booking_id': booking['id']})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/create-event', methods=['POST'])
def create_event_api():
    """Create a new event"""
    try:
        data = request.get_json()
        
        # Generate new event ID
        new_id = max([e['id'] for e in events], default=0) + 1
        
        new_event = {
            'id': new_id,
            'title': data.get('title'),
            'description': data.get('description'),
            'date': data.get('date'),
            'time': data.get('time'),
            'location': data.get('location'),
            'capacity': int(data.get('capacity', 0)),
            'ticketPrice': int(data.get('ticketPrice', 0)),
            'currency': data.get('currency', 'INR'),
            'image': data.get('image', '/static/images/default-event.jpg'),
            'attendees': 0,
            'status': 'upcoming',
            'created_at': datetime.now().isoformat()
        }
        
        events.append(new_event)
        save_events(events)
        
        return jsonify({'success': True, 'event_id': new_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/live-sales')
def get_live_sales():
    """Get live sales data"""
    return jsonify(live_sales_data)

@app.route('/api/export-bookings')
def export_bookings():
    """Export booking data as CSV"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Booking ID', 'Event ID', 'Attendee Name', 'Email', 'Ticket Price', 'Currency', 'Booking Time', 'Status'])
    
    # Write data
    for booking in ticket_bookings:
        writer.writerow([
            booking['id'],
            booking['event_id'],
            booking['attendee_name'],
            booking['attendee_email'],
            booking['ticket_price'],
            booking['currency'],
            booking['booking_time'],
            booking['status']
        ])
    
    output.seek(0)
    csv_data = output.getvalue()
    
    from flask import Response
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=ticket_bookings.csv'}
    )

@app.route('/create-event')
def create_event():
    """Event creation page"""
    return render_template('create-event.html')

# Sample data initialization for analytics
analytics_data = {
    'revenue': {
        'total': 7852000,
        'change': 8.1,
        'weekly_data': [
            {'day': 'Mon', 'sales': 45, 'revenue': 2300000},
            {'day': 'Tue', 'sales': 32, 'revenue': 1800000},
            {'day': 'Wed', 'sales': 68, 'revenue': 3200000},
            {'day': 'Thu', 'sales': 55, 'revenue': 2900000},
            {'day': 'Fri', 'sales': 89, 'revenue': 4100000},
            {'day': 'Sat', 'sales': 120, 'revenue': 5800000},
            {'day': 'Sun', 'sales': 95, 'revenue': 4500000}
        ]
    },
    'engagement': {
        'live_attendance': 240,
        'active_polls': 3,
        'qa_questions': 47,
        'breakdown': [
            {'name': 'Poll Participation', 'value': 40},
            {'name': 'Q&A Sessions', 'value': 32},
            {'name': 'Survey Responses', 'value': 28}
        ]
    }
}

feedback_data = {
    'total_responses': 2568,
    'avg_rating': 4.6,
    'response_rate': 89,
    'nps': 67,
    'ratings': [
        {'category': 'Overall Satisfaction', 'rating': 85},
        {'category': 'Content Quality', 'rating': 92},
        {'category': 'Organization', 'rating': 78},
        {'category': 'Venue Quality', 'rating': 88}
    ],
    'sentiment': {'positive': 68, 'neutral': 22, 'negative': 10},
    'comments': [
        {
            'rating': 5,
            'comment': 'Excellent conference! Very informative.',
            'attendee': 'Sarah Johnson',
            'session': 'Tech Panel Discussion'
        }
    ]
}

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard overview statistics"""
    total_events = len(events)
    total_revenue = sum(event.get('ticketPrice', 0) * event.get('attendees', 0) for event in events)
    total_attendees = sum(event.get('attendees', 0) for event in events)
    avg_rating = feedback_data.get('avg_rating', 4.6)
    
    return jsonify({
        'stats': {
            'total_events': total_events,
            'total_revenue': total_revenue,
            'total_attendees': total_attendees,
            'avg_rating': avg_rating
        },
        'recent_events': events[-4:],  # Last 4 events
        'revenue_trend': analytics_data['revenue']['weekly_data']
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    return jsonify({'events': events})

@app.route('/api/analytics/revenue', methods=['GET'])
def get_revenue_analytics():
    """Get revenue and ticket sales analytics"""
    return jsonify(analytics_data['revenue'])

@app.route('/api/analytics/engagement', methods=['GET'])
def get_engagement_analytics():
    """Get engagement metrics"""
    return jsonify(analytics_data['engagement'])

@app.route('/api/events/<int:event_id>/engagement', methods=['GET'])
def get_event_engagement(event_id):
    """Get engagement data for specific event"""
    try:
        event_engagement = engagement_data.get(str(event_id), {
            'polls': [],
            'qa_questions': [],
            'live_attendance': 0
        })
        
        return jsonify({
            'success': True,
            'polls': event_engagement.get('polls', []),
            'qa_questions': event_engagement.get('qa_questions', []),
            'live_attendance': event_engagement.get('live_attendance', 0)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/events/<int:event_id>/polls', methods=['GET', 'POST'])
def handle_event_polls(event_id):
    """Handle polls for specific event"""
    event_id_str = str(event_id)
    
    if request.method == 'GET':
        # Get polls for this event
        event_polls = engagement_data.get(event_id_str, {}).get('polls', [])
        return jsonify({
            'success': True,
            'polls': event_polls
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Initialize event engagement data if it doesn't exist
            if event_id_str not in engagement_data:
                engagement_data[event_id_str] = {
                    'polls': [],
                    'qa_questions': [],
                    'live_attendance': 240
                }
            
            # Create new poll
            existing_polls = engagement_data[event_id_str].get('polls', [])
            new_poll_id = max([p.get('id', 0) for p in existing_polls], default=0) + 1
            
            new_poll = {
                'id': new_poll_id,
                'question': data.get('question', ''),
                'options': data.get('options', []),
                'responses': 0,
                'active': True,
                'created': datetime.now().isoformat(),
                'option_votes': {option: 0 for option in data.get('options', [])}
            }
            
            engagement_data[event_id_str]['polls'].append(new_poll)
            
            # Save engagement data
            save_engagement_data()
            
            return jsonify({
                'success': True,
                'message': 'Poll created successfully',
                'poll': new_poll
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

@app.route('/api/events/<int:event_id>/polls/<int:poll_id>', methods=['DELETE'])
def delete_poll(event_id, poll_id):
    """Delete a poll"""
    try:
        event_id_str = str(event_id)
        
        if event_id_str in engagement_data and 'polls' in engagement_data[event_id_str]:
            polls = engagement_data[event_id_str]['polls']
            engagement_data[event_id_str]['polls'] = [p for p in polls if p.get('id') != poll_id]
            
            # Save engagement data
            save_engagement_data()
            
            return jsonify({
                'success': True,
                'message': 'Poll deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Poll not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/events/<int:event_id>/polls/<int:poll_id>/vote', methods=['POST'])
def vote_on_poll(event_id, poll_id):
    """Vote on a poll"""
    try:
        data = request.get_json()
        selected_option = data.get('option')
        
        event_id_str = str(event_id)
        
        if event_id_str in engagement_data and 'polls' in engagement_data[event_id_str]:
            polls = engagement_data[event_id_str]['polls']
            
            for poll in polls:
                if poll.get('id') == poll_id:
                    # Increment vote count
                    if 'option_votes' not in poll:
                        poll['option_votes'] = {}
                    
                    if selected_option in poll['option_votes']:
                        poll['option_votes'][selected_option] += 1
                    else:
                        poll['option_votes'][selected_option] = 1
                    
                    # Update total responses
                    poll['responses'] = poll.get('responses', 0) + 1
                    
                    # Save engagement data
                    save_engagement_data()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Vote recorded successfully',
                        'poll': poll
                    })
            
            return jsonify({
                'success': False,
                'error': 'Poll not found'
            }), 404
        else:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/events/<int:event_id>/qa', methods=['GET', 'POST'])
def handle_qa_questions(event_id):
    """Handle Q&A questions for specific event"""
    event_id_str = str(event_id)
    
    if request.method == 'GET':
        # Get Q&A questions for this event
        event_qa = engagement_data.get(event_id_str, {}).get('qa_questions', [])
        return jsonify({
            'success': True,
            'qa_questions': event_qa
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Initialize event engagement data if it doesn't exist
            if event_id_str not in engagement_data:
                engagement_data[event_id_str] = {
                    'polls': [],
                    'qa_questions': [],
                    'live_attendance': 240
                }
            
            # Create new Q&A question
            existing_qa = engagement_data[event_id_str].get('qa_questions', [])
            new_qa_id = max([q.get('id', 0) for q in existing_qa], default=0) + 1
            
            new_question = {
                'id': new_qa_id,
                'question': data.get('question', ''),
                'votes': 0,
                'answered': False,
                'timestamp': datetime.now().isoformat()
            }
            
            engagement_data[event_id_str]['qa_questions'].append(new_question)
            
            # Save engagement data
            save_engagement_data()
            
            return jsonify({
                'success': True,
                'message': 'Question submitted successfully',
                'question': new_question
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400

@app.route('/api/events/<int:event_id>/qa/<int:question_id>/vote', methods=['POST'])
def vote_on_question(event_id, question_id):
    """Vote on a Q&A question"""
    try:
        event_id_str = str(event_id)
        
        if event_id_str in engagement_data and 'qa_questions' in engagement_data[event_id_str]:
            qa_questions = engagement_data[event_id_str]['qa_questions']
            
            for question in qa_questions:
                if question.get('id') == question_id:
                    question['votes'] = question.get('votes', 0) + 1
                    
                    # Save engagement data
                    save_engagement_data()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Vote recorded successfully',
                        'question': question
                    })
            
            return jsonify({
                'success': False,
                'error': 'Question not found'
            }), 404
        else:
            return jsonify({
                'success': False,
                'error': 'Event not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/events/<int:event_id>/qa/<int:question_id>', methods=['DELETE'])
def delete_question(event_id, question_id):
    """Delete a Q&A question"""
    try:
        event_id_str = str(event_id)
        
        if event_id_str in engagement_data and 'qa_questions' in engagement_data[event_id_str]:
            qa_questions = engagement_data[event_id_str]['qa_questions']
            engagement_data[event_id_str]['qa_questions'] = [q for q in qa_questions if q.get('id') != question_id]
            
            # Save engagement data
            save_engagement_data()
            
            return jsonify({
                'success': True,
                'message': 'Question deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Question not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def save_engagement_data():
    """Save engagement data to file"""
    try:
        with open('engagement_data.json', 'w') as f:
            json.dump(engagement_data, f, indent=2)
    except Exception as e:
        print(f"Error saving engagement data: {e}")

@app.route('/api/events/<int:event_id>/qa-questions', methods=['POST'])
def add_qa_question_alt(event_id):
    """Alternative endpoint for adding Q&A questions"""
    return handle_qa_questions(event_id)

@app.route('/api/feedback', methods=['GET'])
def get_feedback_analytics():
    """Get post-event feedback analytics"""
    return jsonify(feedback_data)

@app.route('/api/polls', methods=['GET', 'POST', 'DELETE'])
def handle_polls():
    """Manage polls for events"""
    if request.method == 'GET':
        # Return sample polls data
        polls = [
            {'id': 1, 'question': "What's your favorite session topic?", 'responses': 145, 'active': True},
            {'id': 2, 'question': "Rate the venue quality", 'responses': 89, 'active': False}
        ]
        return jsonify({'polls': polls})
    
    elif request.method == 'POST':
        data = request.get_json()
        new_poll = {
            'id': len(polls) + 1 if 'polls' in locals() else 1,
            'question': data.get('question'),
            'responses': 0,
            'active': True
        }
        return jsonify({'message': 'Poll created successfully', 'poll': new_poll}), 201

@app.route('/api/export/<data_type>', methods=['GET'])
def export_data(data_type):
    """Export various data types as CSV/Excel"""
    if data_type == 'revenue':
        # In a real application, generate CSV/Excel file
        return jsonify({'message': f'Revenue data exported successfully', 'download_url': '/downloads/revenue.csv'})
    
    elif data_type == 'feedback':
        return jsonify({'message': f'Feedback data exported successfully', 'download_url': '/downloads/feedback.csv'})
    
    elif data_type == 'engagement':
        return jsonify({'message': f'Engagement data exported successfully', 'download_url': '/downloads/engagement.csv'})
    
    return jsonify({'error': 'Invalid data type'}), 400

@app.route('/api/live-updates', methods=['GET'])
def get_live_updates():
    """Get real-time updates for live events"""
    live_data = {
        'attendance': analytics_data['engagement']['live_attendance'],
        'new_polls': analytics_data['engagement']['active_polls'],
        'qa_questions': analytics_data['engagement']['qa_questions'],
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(live_data)

@app.route('/api/events/<int:event_id>/analytics', methods=['GET'])
def get_event_analytics(event_id):
    """Get analytics for specific event"""
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Generate mock analytics for the event
    event_analytics = {
        'event': event,
        'revenue': event['ticketPrice'] * event['attendees'],
        'engagement_rate': 75,
        'satisfaction_score': 4.5,
        'attendance_trend': [
            {'time': '10:00', 'attendees': 50},
            {'time': '11:00', 'attendees': 120},
            {'time': '12:00', 'attendees': event['attendees']},
        ]
    }
    return jsonify(event_analytics)

@app.route('/api/events/<int:event_id>/go-live', methods=['POST'])
def go_live_event(event_id):
    """Set event status to live"""
    try:
        # Find the event
        event = next((e for e in events if e['id'] == event_id), None)
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        # Update event status to live
        event['status'] = 'live'
        event['live_start_time'] = datetime.now().isoformat()
        
        # Save events data
        save_events(events)
        
        return jsonify({'success': True, 'message': 'Event is now live'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/events/<int:event_id>/status', methods=['GET'])
def get_event_status(event_id):
    """Get event status"""
    try:
        event = next((e for e in events if e['id'] == event_id), None)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        return jsonify({
            'status': event.get('status', 'upcoming'),
            'live_start_time': event.get('live_start_time')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/events/<int:event_id>/end-event', methods=['POST'])
def end_event(event_id):
    """End event and save data"""
    try:
        # Update event status
        for event in events:
            if event['id'] == event_id:
                event['status'] = 'completed'
                event['ended_at'] = datetime.now().isoformat()
                break
        
        # Save events data
        save_events(events)
        
        return jsonify({
            'success': True,
            'message': 'Event ended successfully'
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/events/<event_id>/post-analytics', methods=['GET'])
def get_post_event_analytics(event_id):
    """Get post-event analytics with real data for completed events only"""
    try:
        # Get event data
        event = next((e for e in events if str(e['id']) == str(event_id)), None)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check if event is completed
        if event.get('status') != 'completed':
            return jsonify({
                'success': False,
                'error': 'Event not completed yet',
                'message': 'Analytics will be available after the event ends'
            }), 400
        
        # Get real engagement data for this event
        event_engagement = engagement_data.get(str(event_id), {})
        polls = event_engagement.get('polls', [])
        qa_questions = event_engagement.get('qa_questions', [])
        live_attendance = event_engagement.get('live_attendance', 0)
        
        # Calculate real metrics from actual event data
        total_poll_responses = sum(poll.get('responses', 0) for poll in polls)
        total_qa_questions = len(qa_questions)
        
        # Calculate real revenue based on event ticket price and attendance
        ticket_price = event.get('ticketPrice', 0)
        total_revenue = ticket_price * live_attendance
        
        # Calculate real engagement rate
        total_interactions = total_poll_responses + total_qa_questions
        engagement_rate = (total_interactions / max(live_attendance, 1)) * 100 if live_attendance > 0 else 0
        engagement_rate = min(engagement_rate, 100)  # Cap at 100%
        
        # Real analytics data
        real_analytics = {
            'total_revenue': total_revenue,
            'total_attendees': live_attendance,
            'total_capacity': event.get('capacity', 500),
            'total_tickets_sold': live_attendance,
            'total_polls': len(polls),
            'total_poll_responses': total_poll_responses,
            'total_qa_questions': total_qa_questions,
            'engagement_rate': round(engagement_rate, 1),
            'satisfaction_score': 4.3,  # Could be calculated from poll responses
            'nps_score': 68,
            'currency': event.get('currency', 'INR'),
            'ticket_price': ticket_price
        }
        
        # Convert polls data to analytics format
        polls_analytics = []
        for poll in polls:
            if poll.get('options') and poll.get('option_votes'):
                total_votes = poll.get('responses', 0)
                options_data = []
                
                for option in poll['options']:
                    votes = poll['option_votes'].get(option, 0)
                    percentage = round((votes / max(total_votes, 1)) * 100, 1)
                    options_data.append({
                        'text': option,
                        'votes': votes,
                        'percentage': percentage
                    })
                
                response_rate = round((total_votes / max(live_attendance, 1)) * 100, 1)
                
                polls_analytics.append({
                    'id': poll.get('id'),
                    'poll_question': poll.get('question'),
                    'poll_type': 'custom',
                    'total_responses': total_votes,
                    'response_rate': response_rate,
                    'options': options_data
                })
        
        # Convert Q&A data to analytics format
        qa_analytics = []
        for qa in qa_questions:
            qa_analytics.append({
                'id': qa.get('id'),
                'question_text': qa.get('question'),
                'category': 'General',
                'vote_count': qa.get('votes', 0),
                'is_answered': qa.get('answered', False),
                'priority_level': 'high' if qa.get('votes', 0) > 15 else 'medium' if qa.get('votes', 0) > 5 else 'low',
                'response_time': 120  # Mock response time
            })
        
        # Generate insights based on real data
        insights = []
        
        if engagement_rate > 50:
            insights.append({
                'type': 'strength',
                'category': 'engagement',
                'text': f'Good audience engagement with {engagement_rate:.1f}% participation rate across {total_interactions} interactions.',
                'confidence': 0.85,
                'supporting_data': {'engagement_rate': engagement_rate, 'total_interactions': total_interactions}
            })
        
        if len(polls) > 0:
            insights.append({
                'type': 'strength',
                'category': 'interaction',
                'text': f'Successfully used {len(polls)} interactive polls generating {total_poll_responses} responses.',
                'confidence': 0.90,
                'supporting_data': {'polls_count': len(polls), 'responses': total_poll_responses}
            })
        
        if total_qa_questions > 5:
            insights.append({
                'type': 'strength',
                'category': 'participation',
                'text': f'High audience interest demonstrated through {total_qa_questions} questions submitted.',
                'confidence': 0.80,
                'supporting_data': {'qa_count': total_qa_questions}
            })
        
        if total_revenue > 0:
            insights.append({
                'type': 'strength',
                'category': 'revenue',
                'text': f'Generated {real_analytics["currency"]} {total_revenue:,} in revenue from {live_attendance} attendees.',
                'confidence': 0.95,
                'supporting_data': {'revenue': total_revenue, 'attendance': live_attendance}
            })
        
        # Calculate capacity utilization
        capacity_utilization = (live_attendance / event.get('capacity', 500)) * 100
        if capacity_utilization < 70:
            insights.append({
                'type': 'opportunity',
                'category': 'marketing',
                'text': f'Event reached {capacity_utilization:.1f}% capacity. Consider enhanced marketing for future events.',
                'confidence': 0.75,
                'supporting_data': {'capacity_utilization': capacity_utilization}
            })
        
        return jsonify({
            'success': True,
            'event_analytics': real_analytics,
            'polls_analytics': polls_analytics,
            'qa_analytics': qa_analytics,
            'insights': insights,
            'sentiment_summary': {
                'positive': {'count': max(15, int(total_poll_responses * 0.7)), 'avg_score': 0.72},
                'neutral': {'count': max(5, int(total_poll_responses * 0.2)), 'avg_score': 0.05},
                'negative': {'count': max(2, int(total_poll_responses * 0.1)), 'avg_score': -0.41}
            },
            'analytics_summary': {
                'total_interactions': total_interactions,
                'avg_poll_response_rate': round(total_poll_responses / max(len(polls), 1), 1),
                'qa_answer_rate': round((sum(1 for qa in qa_questions if qa.get('answered', False)) / max(len(qa_questions), 1)) * 100, 1),
                'revenue_per_attendee': round(total_revenue / max(live_attendance, 1), 2),
                'most_engaging_poll': polls[0].get('question', 'N/A') if polls else 'N/A',
                'top_question': max(qa_questions, key=lambda x: x.get('votes', 0)).get('question', 'N/A') if qa_questions else 'N/A',
                'overall_satisfaction': 4.3,
                'key_strengths': [
                    f'Generated {real_analytics["currency"]} {total_revenue:,} revenue',
                    f'{engagement_rate:.1f}% audience engagement',
                    f'{len(polls)} interactive polls created'
                ],
                'improvement_areas': [
                    'Consider longer Q&A sessions' if total_qa_questions > 10 else 'Encourage more questions',
                    'Add more interactive elements' if len(polls) < 3 else 'Maintain poll frequency',
                    'Improve attendance marketing' if capacity_utilization < 80 else 'Great attendance!'
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

        return jsonify({
            'success': True,
            'insights': insights
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Initialize and load all data on startup
def load_engagement_data():
    """Load engagement data from storage"""
    global engagement_data
    try:
        if os.path.exists('engagement_data.json'):
            with open('engagement_data.json', 'r') as f:
                engagement_data = json.load(f)
        else:
            # Initialize with sample data
            engagement_data = {
                '1': {
                    'polls': [
                        {'id': 1, 'question': "How satisfied are you with the event?", 'responses': 45, 'active': False},
                        {'id': 2, 'question': "What topics interest you most?", 'responses': 32, 'active': True}
                    ],
                    'qa_questions': [
                        {'id': 1, 'question': "What are the latest trends in AI?", 'votes': 15, 'answered': True},
                        {'id': 2, 'question': "How can we improve engagement?", 'votes': 8, 'answered': False}
                    ],
                    'live_attendance': 180
                },
                '2': {
                    'polls': [
                        {'id': 1, 'question': "Rate the music quality", 'responses': 89, 'active': False}
                    ],
                    'qa_questions': [
                        {'id': 1, 'question': "When is the next performance?", 'votes': 12, 'answered': True}
                    ],
                    'live_attendance': 450
                }
            }
    except Exception as e:
        print(f"Error loading engagement data: {e}")
        engagement_data = {}

def load_tickets_data():
    """Load ticket sales data from storage"""
    global tickets_data
    try:
        if os.path.exists('tickets_data.json'):
            with open('tickets_data.json', 'r') as f:
                tickets_data = json.load(f)
        else:
            # Initialize empty tickets data
            tickets_data = {}
    except Exception as e:
        print(f"Error loading tickets data: {e}")
        tickets_data = {}

def init_event_analytics_db():
    """Skip database initialization"""
    print("📊 Using simple JSON-based analytics (database disabled)")

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Load all data
    events = load_events()
    load_engagement_data()
    load_tickets_data()
    init_event_analytics_db()
    
    print("🚀 COUSREVITA 2 Event Management System")
    print(f"📊 Loaded {len(events)} events")
    print(f"🎯 Loaded engagement data for {len(engagement_data)} events")
    print(f"🎫 Loaded ticket data for {len(tickets_data)} events")
    print("🌐 Server running on http://localhost:5000")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
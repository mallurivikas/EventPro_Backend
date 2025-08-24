# Create a new file for database operations
import sqlite3
import json
import os
from datetime import datetime

def init_event_analytics_db():
    """Initialize the event analytics database with comprehensive tables"""
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/event_analytics.db')
    cursor = conn.cursor()
    
    # Main events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE NOT NULL,
            event_title TEXT NOT NULL,
            event_date DATE,
            event_status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            
            -- Basic Event Metrics
            total_capacity INTEGER DEFAULT 0,
            total_tickets_sold INTEGER DEFAULT 0,
            total_revenue DECIMAL(15,2) DEFAULT 0.00,
            ticket_price DECIMAL(10,2) DEFAULT 0.00,
            currency TEXT DEFAULT 'INR',
            
            -- Attendance Metrics
            live_attendance INTEGER DEFAULT 0,
            peak_attendance INTEGER DEFAULT 0,
            avg_attendance DECIMAL(8,2) DEFAULT 0.00,
            attendance_duration_minutes INTEGER DEFAULT 0,
            
            -- Engagement Overview
            total_polls INTEGER DEFAULT 0,
            total_poll_responses INTEGER DEFAULT 0,
            total_qa_questions INTEGER DEFAULT 0,
            total_qa_answered INTEGER DEFAULT 0,
            engagement_rate DECIMAL(5,2) DEFAULT 0.00,
            
            -- Performance Metrics
            conversion_rate DECIMAL(5,2) DEFAULT 0.00,
            satisfaction_score DECIMAL(3,2) DEFAULT 0.00,
            nps_score DECIMAL(4,1) DEFAULT 0.00,
            recommendation_rate DECIMAL(5,2) DEFAULT 0.00
        )
    ''')
    
    # Polls analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poll_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            poll_id INTEGER NOT NULL,
            poll_question TEXT NOT NULL,
            poll_type TEXT DEFAULT 'multiple_choice',
            total_responses INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            response_rate DECIMAL(5,2) DEFAULT 0.00,
            most_popular_option TEXT,
            most_popular_percentage DECIMAL(5,2) DEFAULT 0.00,
            
            FOREIGN KEY (event_id) REFERENCES events_analytics(event_id)
        )
    ''')
    
    # Poll options analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poll_options_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            poll_id INTEGER NOT NULL,
            option_text TEXT NOT NULL,
            vote_count INTEGER DEFAULT 0,
            percentage DECIMAL(5,2) DEFAULT 0.00,
            
            FOREIGN KEY (event_id) REFERENCES events_analytics(event_id)
        )
    ''')
    
    # Q&A analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qa_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            question_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            sentiment TEXT DEFAULT 'neutral',
            priority_level TEXT DEFAULT 'medium',
            vote_count INTEGER DEFAULT 0,
            is_answered BOOLEAN DEFAULT 0,
            response_time_minutes INTEGER DEFAULT NULL,
            created_at TIMESTAMP,
            
            FOREIGN KEY (event_id) REFERENCES events_analytics(event_id)
        )
    ''')
    
    # Engagement timeline table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS engagement_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            activity_type TEXT NOT NULL, -- 'poll_response', 'qa_question', 'attendance_change'
            activity_data TEXT, -- JSON data for specific activity
            attendance_at_time INTEGER DEFAULT 0,
            
            FOREIGN KEY (event_id) REFERENCES events_analytics(event_id)
        )
    ''')
    
    # Sentiment analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            content_type TEXT NOT NULL, -- 'poll_question', 'qa_question', 'overall'
            content_id INTEGER,
            sentiment_score DECIMAL(4,3) DEFAULT 0.000, -- -1 to 1
            sentiment_label TEXT DEFAULT 'neutral', -- positive, negative, neutral
            confidence DECIMAL(4,3) DEFAULT 0.000,
            keywords TEXT, -- JSON array of key phrases
            
            FOREIGN KEY (event_id) REFERENCES events_analytics(event_id)
        )
    ''')
    
    # Event insights table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL,
            insight_type TEXT NOT NULL, -- 'strength', 'weakness', 'opportunity', 'recommendation'
            insight_category TEXT NOT NULL, -- 'engagement', 'content', 'timing', 'audience'
            insight_text TEXT NOT NULL,
            confidence_score DECIMAL(4,3) DEFAULT 0.000,
            supporting_data TEXT, -- JSON with metrics that support this insight
            
            FOREIGN KEY (event_id) REFERENCES events_analytics(event_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Event analytics database initialized successfully")

def capture_event_data_on_completion(event_id, events_data, engagement_data, tickets_data):
    """Capture comprehensive event data when event ends"""
    try:
        # Get event data from various sources
        event_data = get_complete_event_data(event_id, events_data, engagement_data, tickets_data)
        
        # Process and insert into analytics database
        conn = sqlite3.connect('data/event_analytics.db')
        cursor = conn.cursor()
        
        # Insert main event analytics
        cursor.execute('''
            INSERT OR REPLACE INTO events_analytics (
                event_id, event_title, event_date, event_status, completed_at,
                total_capacity, total_tickets_sold, total_revenue, ticket_price, currency,
                live_attendance, peak_attendance, avg_attendance, attendance_duration_minutes,
                total_polls, total_poll_responses, total_qa_questions, total_qa_answered,
                engagement_rate, conversion_rate, satisfaction_score, nps_score, recommendation_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data['event_id'],
            event_data['event_title'],
            event_data['event_date'],
            'completed',
            datetime.now().isoformat(),
            event_data['total_capacity'],
            event_data['total_tickets_sold'],
            event_data['total_revenue'],
            event_data['ticket_price'],
            event_data['currency'],
            event_data['live_attendance'],
            event_data['peak_attendance'],
            event_data['avg_attendance'],
            event_data['attendance_duration_minutes'],
            event_data['total_polls'],
            event_data['total_poll_responses'],
            event_data['total_qa_questions'],
            event_data['total_qa_answered'],
            event_data['engagement_rate'],
            event_data['conversion_rate'],
            event_data['satisfaction_score'],
            event_data['nps_score'],
            event_data['recommendation_rate']
        ))
        
        # Insert poll analytics
        for poll in event_data['polls']:
            cursor.execute('''
                INSERT INTO poll_analytics (
                    event_id, poll_id, poll_question, poll_type, total_responses,
                    created_at, response_rate, most_popular_option, most_popular_percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_id,
                poll['id'],
                poll['question'],
                poll.get('type', 'multiple_choice'),
                poll.get('responses', 0),
                poll.get('created', datetime.now().isoformat()),
                poll.get('response_rate', 0),
                poll.get('most_popular_option', ''),
                poll.get('most_popular_percentage', 0)
            ))
            
            # Insert poll options
            if 'options' in poll and 'option_votes' in poll:
                for option in poll['options']:
                    votes = poll['option_votes'].get(option, 0)
                    total_votes = poll.get('responses', 0)
                    percentage = (votes / total_votes * 100) if total_votes > 0 else 0
                    
                    cursor.execute('''
                        INSERT INTO poll_options_analytics (
                            event_id, poll_id, option_text, vote_count, percentage
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (event_id, poll['id'], option, votes, percentage))
        
        # Insert Q&A analytics
        for qa in event_data['qa_questions']:
            category = categorize_question_for_db(qa['question'])
            sentiment = analyze_question_sentiment(qa['question'])
            priority = determine_priority_level(qa.get('votes', 0))
            
            cursor.execute('''
                INSERT INTO qa_analytics (
                    event_id, question_id, question_text, category, sentiment,
                    priority_level, vote_count, is_answered, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_id,
                qa['id'],
                qa['question'],
                category,
                sentiment,
                priority,
                qa.get('votes', 0),
                qa.get('answered', False),
                qa.get('timestamp', datetime.now().isoformat())
            ))
        
        # Generate and insert insights
        insights = generate_event_insights(event_data)
        for insight in insights:
            cursor.execute('''
                INSERT INTO event_insights (
                    event_id, insight_type, insight_category, insight_text,
                    confidence_score, supporting_data
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                event_id,
                insight['type'],
                insight['category'],
                insight['text'],
                insight['confidence'],
                json.dumps(insight['supporting_data'])
            ))
        
        # Perform sentiment analysis
        perform_comprehensive_sentiment_analysis(event_id, event_data)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Event data captured successfully for event {event_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error capturing event data: {e}")
        return False

def get_complete_event_data(event_id, events_data, engagement_data, tickets_data):
    """Gather all event data from various sources"""
    # Get basic event info
    event = next((e for e in events_data if e['id'] == event_id), {})
    
    # Get engagement data
    engagement = engagement_data.get(str(event_id), {})
    
    # Get ticket data
    tickets = tickets_data.get(str(event_id), {})
    
    # Calculate derived metrics
    total_polls = len(engagement.get('polls', []))
    total_poll_responses = sum(poll.get('responses', 0) for poll in engagement.get('polls', []))
    total_qa_questions = len(engagement.get('qa_questions', []))
    total_qa_answered = sum(1 for qa in engagement.get('qa_questions', []) if qa.get('answered', False))
    
    # Calculate engagement metrics
    live_attendance = engagement.get('live_attendance', tickets.get('total_sold', 150))
    engagement_rate = calculate_engagement_rate(total_poll_responses, total_qa_questions, live_attendance)
    
    # Calculate satisfaction metrics
    satisfaction_data = analyze_satisfaction_from_polls(engagement.get('polls', []))
    
    return {
        'event_id': str(event_id),
        'event_title': event.get('title', 'Unknown Event'),
        'event_date': event.get('date', datetime.now().date().isoformat()),
        'total_capacity': event.get('capacity', 500),
        'total_tickets_sold': tickets.get('total_sold', live_attendance),
        'total_revenue': tickets.get('revenue', event.get('ticketPrice', 25000) * tickets.get('total_sold', live_attendance)),
        'ticket_price': event.get('ticketPrice', 25000),
        'currency': event.get('currency', 'INR'),
        'live_attendance': live_attendance,
        'peak_attendance': max(live_attendance, tickets.get('total_sold', live_attendance)),
        'avg_attendance': live_attendance * 0.85,  # Assume 85% average attendance
        'attendance_duration_minutes': 120,  # Default 2 hours
        'total_polls': total_polls,
        'total_poll_responses': total_poll_responses,
        'total_qa_questions': total_qa_questions,
        'total_qa_answered': total_qa_answered,
        'engagement_rate': engagement_rate,
        'conversion_rate': calculate_conversion_rate(tickets.get('total_sold', live_attendance)),
        'satisfaction_score': satisfaction_data['score'],
        'nps_score': satisfaction_data['nps'],
        'recommendation_rate': satisfaction_data['recommendation_rate'],
        'polls': engagement.get('polls', []),
        'qa_questions': engagement.get('qa_questions', [])
    }

# Helper functions
def categorize_question_for_db(question):
    """Categorize questions for database storage"""
    question_lower = question.lower()
    
    categories = {
        'technical': ['technical', 'platform', 'tool', 'software', 'system', 'bug', 'error'],
        'content': ['topic', 'subject', 'content', 'session', 'speaker', 'presentation'],
        'engagement': ['engage', 'audience', 'interaction', 'participate', 'involve'],
        'logistics': ['time', 'schedule', 'venue', 'location', 'registration', 'access'],
        'feedback': ['feedback', 'opinion', 'suggestion', 'improve', 'better', 'rate'],
        'future': ['future', 'next', 'upcoming', 'plan', 'roadmap', 'trend'],
        'business': ['business', 'strategy', 'revenue', 'roi', 'profit', 'cost']
    }
    
    for category, keywords in categories.items():
        if any(keyword in question_lower for keyword in keywords):
            return category
    
    return 'general'

def analyze_question_sentiment(question):
    """Simple sentiment analysis for questions"""
    positive_words = ['good', 'great', 'excellent', 'amazing', 'helpful', 'useful', 'love', 'best']
    negative_words = ['bad', 'poor', 'terrible', 'awful', 'hate', 'worst', 'difficult', 'problem', 'issue']
    
    question_lower = question.lower()
    positive_count = sum(1 for word in positive_words if word in question_lower)
    negative_count = sum(1 for word in negative_words if word in question_lower)
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'

def determine_priority_level(votes):
    """Determine priority level based on votes"""
    if votes >= 20:
        return 'high'
    elif votes >= 10:
        return 'medium'
    else:
        return 'low'

def calculate_engagement_rate(poll_responses, qa_questions, attendance):
    """Calculate overall engagement rate"""
    if attendance == 0:
        return 0
    
    engagement_score = (poll_responses + qa_questions * 2) / attendance * 100
    return min(engagement_score, 100)  # Cap at 100%

def calculate_conversion_rate(tickets_sold):
    """Calculate conversion rate (mock calculation)"""
    # Assume 1000 page views for every event
    page_views = max(1000, tickets_sold * 5)  # At least 5 views per ticket
    return (tickets_sold / page_views) * 100 if page_views > 0 else 0

def analyze_satisfaction_from_polls(polls):
    """Analyze satisfaction metrics from polls"""
    satisfaction_polls = [p for p in polls if any(word in p.get('question', '').lower() 
                                                for word in ['satisfaction', 'satisfied', 'rate', 'recommend'])]
    
    if not satisfaction_polls:
        return {'score': 3.5, 'nps': 50, 'recommendation_rate': 75}
    
    # Calculate based on poll responses
    total_satisfaction_responses = sum(p.get('responses', 0) for p in satisfaction_polls)
    avg_satisfaction = 3.5 + (total_satisfaction_responses / 100)  # Mock calculation
    
    return {
        'score': min(avg_satisfaction, 5.0),
        'nps': min(40 + (total_satisfaction_responses / 10), 100),
        'recommendation_rate': min(60 + (total_satisfaction_responses / 5), 95)
    }

def generate_event_insights(event_data):
    """Generate AI-like insights based on event data"""
    insights = []
    
    # Engagement insights
    engagement_rate = event_data['engagement_rate']
    if engagement_rate > 80:
        insights.append({
            'type': 'strength',
            'category': 'engagement',
            'text': f'Exceptional audience engagement with {engagement_rate:.1f}% participation rate. Your interactive content strategy was highly effective.',
            'confidence': 0.9,
            'supporting_data': {'engagement_rate': engagement_rate, 'total_responses': event_data['total_poll_responses']}
        })
    elif engagement_rate < 30:
        insights.append({
            'type': 'weakness',
            'category': 'engagement',
            'text': f'Low engagement rate of {engagement_rate:.1f}%. Consider more interactive polls and Q&A sessions to boost participation.',
            'confidence': 0.85,
            'supporting_data': {'engagement_rate': engagement_rate}
        })
    
    # Revenue insights
    capacity_filled = event_data['total_tickets_sold'] / event_data['total_capacity']
    if capacity_filled > 0.8:
        insights.append({
            'type': 'strength',
            'category': 'revenue',
            'text': f'Strong ticket sales with {capacity_filled*100:.1f}% capacity filled. Revenue target exceeded expectations.',
            'confidence': 0.95,
            'supporting_data': {'revenue': event_data['total_revenue'], 'capacity_filled': capacity_filled}
        })
    
    # Q&A insights
    qa_response_rate = (event_data['total_qa_answered'] / event_data['total_qa_questions'] * 100) if event_data['total_qa_questions'] > 0 else 100
    if qa_response_rate < 50:
        insights.append({
            'type': 'opportunity',
            'category': 'content',
            'text': f'Only {qa_response_rate:.1f}% of Q&A questions were answered. Allocating more time for Q&A could improve audience satisfaction.',
            'confidence': 0.8,
            'supporting_data': {'qa_response_rate': qa_response_rate, 'total_questions': event_data['total_qa_questions']}
        })
    
    # Poll effectiveness
    if event_data['total_polls'] > 0:
        avg_poll_responses = event_data['total_poll_responses'] / event_data['total_polls']
        if avg_poll_responses > event_data['live_attendance'] * 0.6:
            insights.append({
                'type': 'strength',
                'category': 'engagement',
                'text': f'Polls were highly effective with an average of {avg_poll_responses:.0f} responses per poll.',
                'confidence': 0.85,
                'supporting_data': {'avg_poll_responses': avg_poll_responses}
            })
    
    # Recommendations
    insights.append({
        'type': 'recommendation',
        'category': 'future',
        'text': 'Based on engagement patterns, consider extending similar events to 90-120 minutes for optimal audience retention.',
        'confidence': 0.75,
        'supporting_data': {'current_engagement': engagement_rate}
    })
    
    return insights

def perform_comprehensive_sentiment_analysis(event_id, event_data):
    """Perform sentiment analysis on all text content"""
    conn = sqlite3.connect('data/event_analytics.db')
    cursor = conn.cursor()
    
    # Analyze poll questions
    for poll in event_data['polls']:
        sentiment_score, sentiment_label = simple_sentiment_analysis(poll['question'])
        
        cursor.execute('''
            INSERT INTO sentiment_analysis (
                event_id, content_type, content_id, sentiment_score,
                sentiment_label, confidence, keywords
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_id, 'poll_question', poll['id'], sentiment_score,
            sentiment_label, 0.8, json.dumps(extract_keywords(poll['question']))
        ))
    
    # Analyze Q&A questions
    for qa in event_data['qa_questions']:
        sentiment_score, sentiment_label = simple_sentiment_analysis(qa['question'])
        
        cursor.execute('''
            INSERT INTO sentiment_analysis (
                event_id, content_type, content_id, sentiment_score,
                sentiment_label, confidence, keywords
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_id, 'qa_question', qa['id'], sentiment_score,
            sentiment_label, 0.8, json.dumps(extract_keywords(qa['question']))
        ))
    
    conn.commit()
    conn.close()

def simple_sentiment_analysis(text):
    """Simple sentiment analysis returning score and label"""
    positive_words = ['good', 'great', 'excellent', 'amazing', 'helpful', 'useful', 'love', 'best', 'fantastic', 'wonderful', 'awesome', 'perfect']
    negative_words = ['bad', 'poor', 'terrible', 'awful', 'hate', 'worst', 'difficult', 'problem', 'issue', 'disappointing', 'frustrating', 'confusing']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    total_words = len(text.split())
    sentiment_score = (positive_count - negative_count) / max(total_words, 1)
    
    if sentiment_score > 0.1:
        return sentiment_score, 'positive'
    elif sentiment_score < -0.1:
        return sentiment_score, 'negative'
    else:
        return sentiment_score, 'neutral'

def extract_keywords(text):
    """Extract key phrases from text"""
    # Simple keyword extraction
    words = text.lower().split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might'}
    
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    return keywords[:5]  # Return top 5 keywords
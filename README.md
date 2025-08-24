# Event Analytics Dashboard

A modern, responsive Event Analytics Dashboard for event hosts built with Flask and HTML templates.

## Features

- **Dashboard Overview**: Total events, revenue, attendees, and ratings
- **Event Creation**: Create and manage events with detailed information
- **Revenue Analytics**: Track ticket sales and revenue with interactive charts
- **Live Engagement**: Monitor real-time attendance, polls, and Q&A sessions
- **Post-Event Feedback**: Analyze attendee feedback and satisfaction ratings
- **Data Export**: Export analytics data as CSV/Excel files

## Frontend Deployment Link (For UI Demonstration)
https://mallurivikas.github.io/EventPro_Frontend/

## Tech Stack

**Frontend:**
- HTML5 Templates (Jinja2)
- Tailwind CSS (via CDN)
- Chart.js (data visualization)
- Lucide Icons

**Backend:**
- Flask
- Flask-CORS

## Installation

### Quick Start

1. Navigate to the project directory:
```bash
cd "c:\Users\vikas\OneDrive\Desktop\COUSREVITA 2"
```

2. Run the cleanup script (optional - removes old React files):
```bash
cleanup_react_files.bat
```

3. Start the application:
```bash
cd backend
start_backend.bat
```

The application will be available at `http://localhost:5000`

### Manual Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the Flask server:
```bash
python app.py
```

The application will run on `http://localhost:5000`

## API Endpoints

- `GET /api/dashboard` - Get dashboard statistics
- `GET /api/events` - Get all events
- `POST /api/events` - Create new event
- `GET /api/analytics/revenue` - Get revenue analytics
- `GET /api/analytics/engagement` - Get engagement metrics
- `GET /api/feedback` - Get feedback analytics
- `GET /api/polls` - Get polls data
- `POST /api/polls` - Create new poll
- `GET /api/export/<data_type>` - Export data
- `GET /api/live-updates` - Get real-time updates

## Usage

1. **Home Page**: Visit `http://localhost:5000/` to see the landing page with app details
2. **Login**: Use the demo credentials (demo@eventpro.com / demo123) to access the dashboard
3. **Dashboard**: View overall statistics and recent events at `http://localhost:5000/dashboard`
4. **Create Event**: Fill in event details at `http://localhost:5000/create-event`
5. **Revenue & Sales**: Track pre-event analytics at `http://localhost:5000/analytics`
6. **Engagement Metrics**: Monitor live engagement at `http://localhost:5000/engagement`
7. **Feedback**: Analyze post-event feedback at `http://localhost:5000/feedback`
8. **Export**: Download analytics data for further analysis

## Demo Credentials

- **Email**: demo@eventpro.com
- **Password**: demo123

## Project Structure

```
COUSREVITA 2/
├── templates/
│   ├── base.html
│   ├── home.html (landing page with login)
│   ├── dashboard.html
│   ├── create-event.html
│   ├── analytics.html
│   ├── engagement.html
│   └── feedback.html
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── start_backend.bat
├── cleanup_react_files.bat
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

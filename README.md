# Campus Event Planning & RSVP App
A web application that allows students to discover campus events, submit RSVPs, join waitlists, receive notifications, and view attendance history. Organizers can create and manage events, review attendees, and record attendance.

## Features

### Students
- Create an account and log in
- Browse and search upcoming events
- View event details
- RSVP or join an event waitlist
- Cancel an RSVP
- View RSVP and attendance history
- Receive event updates, reminders, cancellations, and waitlist notifications

### Organizers
- Create an account and log in
- Create, edit, and cancel events
- View events on the organizer dashboard
- Review registered and waitlisted attendees
- Check attendees in
- Monitor recent RSVPs

## Technologies
- **Frontend:** HTML, CSS, and JavaScript
- **Backend:** Python and Flask
- **Database:** SQLite
- **Authentication:** JSON Web Tokens
- **Testing:** Pytest

## Requirements
Before running the application, install:
- Python 3.9 or newer
- Git
- A modern web browser

Node.js & npm aren't required.

## Initial Setup
Clone the repository & enter the project directory:

```bash
git clone https://github.com/DevaunThomas/CIS_376_RSVP_App.git
cd CIS_376_RSVP_App
```

Create a virtual environment.

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running the Application
The frontend & backend must run at the same time. Keep both terminal windows open while using the application.

### Windows Quick Start
Activate the virtual environment from the project root, then run:

```powershell
.\start.ps1
```

This script:
1. Starts the Flask backend on port `5000`
2. Starts the frontend server on port `5500`
3. Opens the application in the default browser

If the browser doesn't open automatically, visit:

```text
http://localhost:5500
```

### macOS or Linux
Open a terminal in the project root & activate the virtual environment:

```bash
source .venv/bin/activate
```

Start the backend:

```bash
cd backend
python app.py
```

Leave that terminal open.

Open a second terminal, return to the project folder, & start the frontend:

```bash
cd frontend
python3 -m http.server 5500
```

Open the application at:

```text
http://localhost:5500
```

## Manual Windows Start

If `start.ps1` cannot be used, start each server manually.

In the first PowerShell window:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python app.py
```

In a second PowerShell window:

```powershell
cd frontend
python -m http.server 5500
```

Then visit:

```text
http://localhost:5500
```

## Stopping the Application

Press `Ctrl+C` in each terminal running a server.

If `start.ps1` opened separate PowerShell windows, close both server windows when finished.

## Important Notes
- Don't open `frontend/index.html` directly from the file system.
- Always access the frontend through `http://localhost:5500`.
- The backend must be running for login, registration, events, RSVPs, attendance, and notifications to work.
- The SQLite database is stored at `backend/campus_events.db`.
- New users can create student or organizer accounts from the registration page.
- The frontend automatically connects to `http://127.0.0.1:5000/api` during local development.

## Branch Workflow

Create a personal branch before making changes:

```bash
git checkout -b YourBranchName
```

Commit changes to your own branch & share completed updates with the team. Only reviewed & approved changes should be merged into `main`.

## Project Structure

```text
CIS_376_RSVP_App/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── campus_events.db
│   ├── schema.sql
│   ├── models/
│   │   ├── attendance.py
│   │   ├── event.py
│   │   ├── notification.py
│   │   ├── rsvp.py
│   │   └── user.py
│   ├── routes/
│   │   ├── attendance_routes.py
│   │   ├── event_routes.py
│   │   ├── notification_routes.py
│   │   ├── rsvp_routes.py
│   │   └── user_routes.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── limiter.py
│   │   ├── notification_service.py
│   │   ├── reminder_service.py
│   │   └── validation_service.py
│   └── tests/
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── config.js
│   ├── assets/
│   ├── components/
│   ├── data/
│   ├── pages/
│   └── utils/
├── requirements.txt
├── start.ps1
└── README.md
```

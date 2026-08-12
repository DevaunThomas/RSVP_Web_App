# CIS_376_RSVP_App
An app developed for CIS 376 that will handle Event Planning and RSVPs.

App will be developed in Visual Studio Code. 
Frontend will be written in HTML, CSS, or JavaScript.
Backend will be written in Python with a Django framework to handle event creation, RSVP processing, user accounts, and organizer features.
SQLite database will store event details, user information, RSVP records, attendance status, and notification data.

## Before You Begin (PLEASE READ):
Please create your own branch with your name as the branch name. This will be where you make your changes and edits. Only changes that are approved by the group will be committed to the main branch. This will prevent people working on top of eachother and will give us updated starting points in case a branch breaks and someone needs to repull everything. If multiple people are working on a certain part (backend or frontend), please communicate with each other so that your changes are working together. Lastly, any updates you make to your branch should be shared in the groupchat so all members are up-to-date with each other.

## To run program:
From the root folder, use command: .\start.ps1
A new powershell window may open. Leave it open as it has the backend running there.

## App Structure:

```
campus-event-rsvp-app/
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   ├── assets/
│   │   └── um-dearborn-logo.webp
│   │
│   ├── pages/
│   │   ├── createEvent.js
│   │   ├── eventDetails.js
│   │   ├── events.js
│   │   ├── login.js
│   │   ├── organizerDashboard.js
│   │   ├── register.js
│   │   ├── rsvp.js
│   │   └── studentDashboard.js
│   │
│   └── components/
│       ├── eventCard.js
│       ├── footer.js
│       ├── navbar.js
│       └── rsvpButton.js
│
├── backend/
│   ├── app.py
│   ├── routes/
│   │   ├── event_routes.py
│   │   ├── rsvp_routes.py
│   │   └── user_routes.py
│   │
│   ├── models/
│   │   ├── event.py
│   │   ├── user.py
│   │   └── rsvp.py
│   │
│   └── services/
│       ├── notification_service.py
│       └── reminder_service.py
│
├── database/
│   └── campus_events.db
│
├── README.md
└── requirements.txt
```

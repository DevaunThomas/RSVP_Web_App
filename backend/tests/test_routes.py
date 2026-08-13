import os
import tempfile
import sys
import pytest

# Add backend directory to path so imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create a temp database file and set it in environment variables
# BEFORE importing app and config. This makes config.py load our temp database.
db_fd, temp_db_path = tempfile.mkstemp()
os.environ["DATABASE_PATH"] = temp_db_path
os.environ["FLASK_ENV"] = "testing"

from app import create_app
from database import DatabaseHelper
from models.user import User
from models.event import Event
from models.rsvp import RSVP
from services.auth_service import generate_token
from services.reminder_service import ReminderService


@pytest.fixture(scope="module")
def app():
    # Initialize the database schema for the test database
    DatabaseHelper.init_db()

    app = create_app()
    yield app

    # Clean up the test database file
    os.close(db_fd)
    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except OSError:
            pass


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_database_tables():
    """
    Cleans up the database tables between tests to ensure a clean state
    without recreating the database schema.
    """
    # Disable foreign key checks momentarily to truncate safely
    DatabaseHelper.execute_write("PRAGMA foreign_keys = OFF;")
    DatabaseHelper.execute_write("DELETE FROM Attendance;")
    DatabaseHelper.execute_write("DELETE FROM Notifications;")
    DatabaseHelper.execute_write("DELETE FROM RSVPs;")
    DatabaseHelper.execute_write("DELETE FROM Events;")
    DatabaseHelper.execute_write("DELETE FROM Users;")
    DatabaseHelper.execute_write("PRAGMA foreign_keys = ON;")


def get_auth_headers(user_id: int, role: str, name: str = "Test User", email: str = "test@campus.edu"):
    """Generates Authorization header dict for testing."""
    token = generate_token(user_id, role, name, email)
    return {"Authorization": f"Bearer {token}"}


def test_home_route(client):
    """Test that the home route displays the running message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "Campus Event RSVP API is running" in data["message"]


def test_404_route(client):
    """Test that non-existent routes return a 404 error response."""
    response = client.get("/api/non_existent_route")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Route not found"


def test_auth_login_logout_and_me(client):
    """Test user registration, login, token retrieval, /me profile, and logout."""
    # 1. Register User
    reg_response = client.post("/api/users", json={
        "name": "Alice Security",
        "email": "alice@campus.edu",
        "password": "securepassword123",
        "role": "student"
    })
    assert reg_response.status_code == 201
    reg_data = reg_response.get_json()
    assert "token" in reg_data
    user_id = reg_data["user_id"]

    # 2. Login with valid credentials
    login_res = client.post("/api/login", json={
        "email": "alice@campus.edu",
        "password": "securepassword123"
    })
    assert login_res.status_code == 200
    login_data = login_res.get_json()
    assert login_data["message"] == "Login successful"
    token = login_data["token"]
    assert login_data["user"]["email"] == "alice@campus.edu"

    # 3. Login with invalid password
    bad_pass_res = client.post("/api/login", json={
        "email": "alice@campus.edu",
        "password": "wrongpassword"
    })
    assert bad_pass_res.status_code == 401
    assert "Invalid email or password" in bad_pass_res.get_json()["error"]

    # 4. Access /me endpoint with token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.get_json()["email"] == "alice@campus.edu"

    # 5. Access /me endpoint without token -> 401
    me_unauth = client.get("/api/me")
    assert me_unauth.status_code == 401

    # 6. Logout endpoint
    logout_res = client.post("/api/logout")
    assert logout_res.status_code == 200


def test_user_lifecycle(client):
    """Test creating, reading, updating, and deleting users with authentication headers."""
    # 1. Create a Student
    response = client.post("/api/users", json={
        "name": "Jane Student",
        "email": "jane@campus.edu",
        "password": "studentpassword123",
        "role": "student"
    })
    assert response.status_code == 201
    student_data = response.get_json()
    assert student_data["message"] == "User created successfully"
    student_id = student_data["user_id"]
    student_headers = get_auth_headers(student_id, "student", "Jane Student", "jane@campus.edu")

    # 2. Create an Organizer
    response = client.post("/api/users", json={
        "name": "Bob Organizer",
        "email": "bob@campus.edu",
        "password": "organizerpassword123",
        "role": "organizer"
    })
    assert response.status_code == 201
    organizer_data = response.get_json()
    organizer_id = organizer_data["user_id"]
    organizer_headers = get_auth_headers(organizer_id, "organizer", "Bob Organizer", "bob@campus.edu")

    # 3. Validation: Try to register with duplicate email
    response = client.post("/api/users", json={
        "name": "Another Jane",
        "email": "jane@campus.edu",
        "password": "diffpassword",
        "role": "student"
    })
    assert response.status_code == 409
    assert "exists" in response.get_json()["error"]

    # 4. Validation: Try to register with missing fields
    response = client.post("/api/users", json={
        "name": "Missing Email User",
        "password": "password",
        "role": "student"
    })
    assert response.status_code == 400
    assert "email" in response.get_json()["fields"]

    # 5. Validation: Try to register with invalid role
    response = client.post("/api/users", json={
        "name": "Admin User",
        "email": "admin@campus.edu",
        "password": "password",
        "role": "admin"
    })
    assert response.status_code == 400
    assert "Role must be student or organizer" in response.get_json()["error"]

    # 6. Read All Users (requires token)
    response = client.get("/api/users", headers=student_headers)
    assert response.status_code == 200
    users = response.get_json()
    assert len(users) == 2
    emails = [u["email"] for u in users]
    assert "jane@campus.edu" in emails
    assert "bob@campus.edu" in emails

    # 7. Read Specific User
    response = client.get(f"/api/users/{student_id}", headers=student_headers)
    assert response.status_code == 200
    user = response.get_json()
    assert user["name"] == "Jane Student"
    assert user["role"] == "student"

    # 8. Update User
    response = client.put(f"/api/users/{student_id}", json={
        "name": "Jane Student Updated",
        "email": "jane_updated@campus.edu",
        "role": "student"
    }, headers=student_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "User updated successfully"

    # Verify update
    response = client.get(f"/api/users/{student_id}", headers=student_headers)
    assert response.get_json()["name"] == "Jane Student Updated"
    assert response.get_json()["email"] == "jane_updated@campus.edu"

    # 9. Delete User
    response = client.delete(f"/api/users/{student_id}", headers=student_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "User deleted successfully"

    # Verify deletion
    response = client.get(f"/api/users/{student_id}", headers=organizer_headers)
    assert response.status_code == 404


def test_event_lifecycle(client):
    """Test creating, fetching, updating, canceling, and deleting events with authorization rules."""
    # Setup: Create an organizer and a student user
    org_response = client.post("/api/users", json={
        "name": "Event Organizer",
        "email": "org@campus.edu",
        "password": "password",
        "role": "organizer"
    })
    organizer_id = org_response.get_json()["user_id"]
    org_headers = get_auth_headers(organizer_id, "organizer", "Event Organizer", "org@campus.edu")

    stu_response = client.post("/api/users", json={
        "name": "Regular Student",
        "email": "student@campus.edu",
        "password": "password",
        "role": "student"
    })
    student_id = stu_response.get_json()["user_id"]
    student_headers = get_auth_headers(student_id, "student", "Regular Student", "student@campus.edu")

    # 1. Create a Valid Event (with organizer auth)
    response = client.post("/api/events", json={
        "title": "Welcome Back BBQ",
        "description": "Free food and drinks for all students!",
        "event_date": "2026-09-10",
        "event_time": "12:00:00",
        "location": "Campus Quad",
        "capacity": 100,
        "organizer_id": organizer_id
    }, headers=org_headers)
    assert response.status_code == 201
    event_data = response.get_json()
    assert event_data["message"] == "Event created successfully"
    event_id = event_data["event_id"]

    # 2. Validation: Try to create event with a student token -> 403 Forbidden
    response = client.post("/api/events", json={
        "title": "Student Run Party",
        "event_date": "2026-09-10",
        "event_time": "20:00:00",
        "location": "Dorm Hall",
        "capacity": 20,
        "organizer_id": student_id
    }, headers=student_headers)
    assert response.status_code == 403
    assert "Organizer access required" in response.get_json()["error"]

    # 3. Validation: Try to create event without token -> 401 Unauthorized
    response = client.post("/api/events", json={
        "title": "Unauthenticated Event",
        "event_date": "2026-09-10",
        "event_time": "20:00:00",
        "location": "Unknown",
        "capacity": 10
    })
    assert response.status_code == 401

    # 4. Validation: Try to create event with negative capacity
    response = client.post("/api/events", json={
        "title": "Negative Capacity Event",
        "event_date": "2026-09-10",
        "event_time": "20:00:00",
        "location": "Dorm Hall",
        "capacity": -5,
        "organizer_id": organizer_id
    }, headers=org_headers)
    assert response.status_code == 400
    assert "Capacity must be a positive integer" in response.get_json()["error"]

    # 5. Fetch Active Events (Public route, no token required)
    response = client.get("/api/events")
    assert response.status_code == 200
    events = response.get_json()
    assert len(events) == 1
    assert events[0]["title"] == "Welcome Back BBQ"

    # 6. Fetch Event by ID (Public route, no token required)
    response = client.get(f"/api/events/{event_id}")
    assert response.status_code == 200
    event = response.get_json()
    assert event["title"] == "Welcome Back BBQ"
    assert event["registered_count"] == 0

    # 7. Update Event (organizer owner)
    response = client.put(f"/api/events/{event_id}", json={
        "title": "Welcome Back BBQ - Updated",
        "description": "Now with vegetarian options!",
        "event_date": "2026-09-11",
        "event_time": "13:00:00",
        "location": "Campus Center",
        "capacity": 150,
        "status": "Updated"
    }, headers=org_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Event updated successfully"

    # Verify event update
    response = client.get(f"/api/events/{event_id}")
    event = response.get_json()
    assert event["title"] == "Welcome Back BBQ - Updated"
    assert event["capacity"] == 150
    assert event["location"] == "Campus Center"

    # 8. Cancel Event
    response = client.patch(f"/api/events/{event_id}/cancel", headers=org_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Event canceled successfully"

    # Active events endpoint should not contain canceled events by default
    response = client.get("/api/events")
    assert len(response.get_json()) == 0

    # Active events endpoint should contain canceled events if include_canceled=true is sent
    response = client.get("/api/events?include_canceled=true")
    assert len(response.get_json()) == 1
    assert response.get_json()[0]["status"] == "Canceled"

    # 9. Delete Event
    response = client.delete(f"/api/events/{event_id}", headers=org_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Event deleted successfully"

    # Verify deletion
    response = client.get(f"/api/events/{event_id}")
    assert response.status_code == 404


def test_rsvp_and_waitlist_flow(client):
    """Test RSVP flow including capacity checks, waitlisting, and token security."""
    # Setup: Create an organizer, a small capacity event, and three students
    org_res = client.post("/api/users", json={
        "name": "Org", "email": "o@campus.edu", "password": "p", "role": "organizer"
    })
    organizer_id = org_res.get_json()["user_id"]
    org_headers = get_auth_headers(organizer_id, "organizer")

    stu1_res = client.post("/api/users", json={
        "name": "Student A", "email": "a@campus.edu", "password": "p", "role": "student"
    })
    student1_id = stu1_res.get_json()["user_id"]
    stu1_headers = get_auth_headers(student1_id, "student", "Student A", "a@campus.edu")

    stu2_res = client.post("/api/users", json={
        "name": "Student B", "email": "b@campus.edu", "password": "p", "role": "student"
    })
    student2_id = stu2_res.get_json()["user_id"]
    stu2_headers = get_auth_headers(student2_id, "student", "Student B", "b@campus.edu")

    stu3_res = client.post("/api/users", json={
        "name": "Student C", "email": "c@campus.edu", "password": "p", "role": "student"
    })
    student3_id = stu3_res.get_json()["user_id"]
    stu3_headers = get_auth_headers(student3_id, "student", "Student C", "c@campus.edu")

    # Create event with capacity of 2
    event_res = client.post("/api/events", json={
        "title": "Exclusive Seminar",
        "description": "Max capacity 2",
        "event_date": "2026-11-20",
        "event_time": "10:00:00",
        "location": "Room 204",
        "capacity": 2,
        "organizer_id": organizer_id
    }, headers=org_headers)
    event_id = event_res.get_json()["event_id"]

    # 1. First student RSVPs -> Registered
    response = client.post("/api/rsvps", json={
        "user_id": student1_id,
        "event_id": event_id
    }, headers=stu1_headers)
    assert response.status_code == 201
    assert response.get_json()["rsvp_status"] == "Registered"
    rsvp1_id = response.get_json()["rsvp_id"]

    # 2. Second student RSVPs -> Registered
    response = client.post("/api/rsvps", json={
        "user_id": student2_id,
        "event_id": event_id
    }, headers=stu2_headers)
    assert response.status_code == 201
    assert response.get_json()["rsvp_status"] == "Registered"

    # 3. Third student RSVPs -> Waitlisted (since capacity is 2)
    response = client.post("/api/rsvps", json={
        "user_id": student3_id,
        "event_id": event_id
    }, headers=stu3_headers)
    assert response.status_code == 201
    assert response.get_json()["rsvp_status"] == "Waitlisted"
    rsvp3_id = response.get_json()["rsvp_id"]

    # Verify event's registered count remains 2
    event_info = client.get(f"/api/events/{event_id}").get_json()
    assert event_info["registered_count"] == 2

    # 4. Duplicate RSVP -> 409 Conflict
    response = client.post("/api/rsvps", json={
        "user_id": student1_id,
        "event_id": event_id
    }, headers=stu1_headers)
    assert response.status_code == 409
    assert response.get_json()["error"] == "User has already responded to this event"

    # 5. Fetch RSVPs for Event
    response = client.get(f"/api/events/{event_id}/rsvps", headers=org_headers)
    assert response.status_code == 200
    rsvps = response.get_json()
    assert len(rsvps) == 3
    assert any(r["name"] == "Student A" and r["rsvp_status"] == "Registered" for r in rsvps)
    assert any(r["name"] == "Student C" and r["rsvp_status"] == "Waitlisted" for r in rsvps)

    # 6. Fetch RSVPs for User
    response = client.get(f"/api/users/{student3_id}/rsvps", headers=stu3_headers)
    assert response.status_code == 200
    user_rsvps = response.get_json()
    assert len(user_rsvps) == 1
    assert user_rsvps[0]["title"] == "Exclusive Seminar"
    assert user_rsvps[0]["rsvp_status"] == "Waitlisted"

    # 7. Cancel RSVP
    response = client.patch(f"/api/rsvps/{rsvp1_id}/cancel", headers=stu1_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "RSVP canceled successfully"

    # Verify status changed to Canceled
    rsvp1_status = client.get(f"/api/rsvps/{rsvp1_id}", headers=stu1_headers).get_json()
    assert rsvp1_status["rsvp_status"] == "Canceled"

    # 8. Delete RSVP
    response = client.delete(f"/api/rsvps/{rsvp3_id}", headers=stu3_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "RSVP deleted successfully"

    # Verify deletion
    response = client.get(f"/api/rsvps/{rsvp3_id}", headers=stu3_headers)
    assert response.status_code == 404


def test_attendance_flow(client):
    """Test attendance flow with security authorization (check-in, listing, toggling, and deletion)."""
    # Setup: Create organizer, event, student with registered RSVP, student with waitlisted RSVP, student with no RSVP
    org_res = client.post("/api/users", json={
        "name": "Org2", "email": "o2@campus.edu", "password": "p", "role": "organizer"
    })
    organizer_id = org_res.get_json()["user_id"]
    org_headers = get_auth_headers(organizer_id, "organizer", "Org2", "o2@campus.edu")

    # Student 1: will have Registered RSVP
    stu1_res = client.post("/api/users", json={
        "name": "Attendee A", "email": "att_a@campus.edu", "password": "p", "role": "student"
    })
    student1_id = stu1_res.get_json()["user_id"]
    stu1_headers = get_auth_headers(student1_id, "student", "Attendee A", "att_a@campus.edu")

    # Student 2: will have Waitlisted RSVP
    stu2_res = client.post("/api/users", json={
        "name": "Attendee B", "email": "att_b@campus.edu", "password": "p", "role": "student"
    })
    student2_id = stu2_res.get_json()["user_id"]
    stu2_headers = get_auth_headers(student2_id, "student", "Attendee B", "att_b@campus.edu")

    # Student 3: no RSVP at all
    stu3_res = client.post("/api/users", json={
        "name": "Attendee C", "email": "att_c@campus.edu", "password": "p", "role": "student"
    })
    student3_id = stu3_res.get_json()["user_id"]
    stu3_headers = get_auth_headers(student3_id, "student", "Attendee C", "att_c@campus.edu")

    # Event with capacity of 1
    event_res = client.post("/api/events", json={
        "title": "Tiny Event",
        "description": "Cap 1",
        "event_date": "2026-12-01",
        "event_time": "15:00:00",
        "location": "Room 10",
        "capacity": 1,
        "organizer_id": organizer_id
    }, headers=org_headers)
    event_id = event_res.get_json()["event_id"]

    # RSVP Student 1 -> Registered
    client.post("/api/rsvps", json={"user_id": student1_id, "event_id": event_id}, headers=stu1_headers)
    # RSVP Student 2 -> Waitlisted
    client.post("/api/rsvps", json={"user_id": student2_id, "event_id": event_id}, headers=stu2_headers)

    # 1. Deny check-in for user with no RSVP
    response = client.post(f"/api/events/{event_id}/check-in", json={"user_id": student3_id}, headers=stu3_headers)
    assert response.status_code == 400
    assert "must have a 'Registered' RSVP" in response.get_json()["error"]

    # 2. Deny check-in for waitlisted user
    response = client.post(f"/api/events/{event_id}/check-in", json={"user_id": student2_id}, headers=stu2_headers)
    assert response.status_code == 400
    assert "must have a 'Registered' RSVP" in response.get_json()["error"]

    # 3. Successful check-in for registered user
    response = client.post(f"/api/events/{event_id}/check-in", json={"user_id": student1_id}, headers=stu1_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Check-in successful"

    # Verify check-in record details (organizer access)
    response = client.get(f"/api/events/{event_id}/attendance", headers=org_headers)
    assert response.status_code == 200
    attendance = response.get_json()
    assert len(attendance) == 1
    assert attendance[0]["user_id"] == student1_id
    assert attendance[0]["attended"] == 1
    assert attendance[0]["check_in_time"] is not None

    # Verify check-in under user's attendance list
    response = client.get(f"/api/users/{student1_id}/attendance", headers=stu1_headers)
    assert response.status_code == 200
    user_attendance = response.get_json()
    assert len(user_attendance) == 1
    assert user_attendance[0]["event_id"] == event_id
    assert user_attendance[0]["attended"] == 1

    # 4. Manual update: mark attended as false (organizer access)
    response = client.patch(f"/api/events/{event_id}/attendance/{student1_id}", json={"attended": False}, headers=org_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Attendance status updated successfully"

    # Verify updated state
    response = client.get(f"/api/events/{event_id}/attendance", headers=org_headers)
    assert response.get_json()[0]["attended"] == 0

    # 5. Manual update: deny marking True if not registered (e.g. waitlisted student 2)
    response = client.patch(f"/api/events/{event_id}/attendance/{student2_id}", json={"attended": True}, headers=org_headers)
    assert response.status_code == 400
    assert "must have a 'Registered' RSVP" in response.get_json()["error"]

    # 6. Deletion of attendance record
    response = client.delete(f"/api/events/{event_id}/attendance/{student1_id}", headers=org_headers)
    assert response.status_code == 200
    assert response.get_json()["message"] == "Attendance record deleted successfully"

    # Verify deleted
    response = client.get(f"/api/events/{event_id}/attendance", headers=org_headers)
    assert len(response.get_json()) == 0

    # 7. Deny check-in for canceled event
    event_res2 = client.post("/api/events", json={
        "title": "Cancel Checkin Event",
        "description": "Temp event",
        "event_date": "2026-12-05",
        "event_time": "15:00:00",
        "location": "Room 11",
        "capacity": 10,
        "organizer_id": organizer_id
    }, headers=org_headers)
    event_id2 = event_res2.get_json()["event_id"]
    client.post("/api/rsvps", json={"user_id": student1_id, "event_id": event_id2}, headers=stu1_headers)

    # Cancel event
    client.patch(f"/api/events/{event_id2}/cancel", headers=org_headers)

    # Attempt check-in
    response = client.post(f"/api/events/{event_id2}/check-in", json={"user_id": student1_id}, headers=stu1_headers)
    assert response.status_code == 400
    assert "Cannot check in to a canceled event" in response.get_json()["error"]


def test_notifications_and_reminders_flow(client):
    """Test notification creation, automated triggers on event update/cancel, API management, and reminders."""
    # Setup organizer and student
    org_res = client.post("/api/users", json={
        "name": "Notif Org", "email": "notif_org@campus.edu", "password": "p", "role": "organizer"
    })
    organizer_id = org_res.get_json()["user_id"]
    org_headers = get_auth_headers(organizer_id, "organizer", "Notif Org", "notif_org@campus.edu")

    stu_res = client.post("/api/users", json={
        "name": "Notif Student", "email": "notif_stu@campus.edu", "password": "p", "role": "student"
    })
    student_id = stu_res.get_json()["user_id"]
    stu_headers = get_auth_headers(student_id, "student", "Notif Student", "notif_stu@campus.edu")

    # Create event and RSVP
    event_res = client.post("/api/events", json={
        "title": "Tech Talk",
        "description": "Intro to Tech",
        "event_date": "2026-10-10",
        "event_time": "14:00:00",
        "location": "Hall A",
        "capacity": 50,
        "organizer_id": organizer_id
    }, headers=org_headers)
    event_id = event_res.get_json()["event_id"]

    client.post("/api/rsvps", json={"user_id": student_id, "event_id": event_id}, headers=stu_headers)

    # 1. Update event -> Should trigger automated 'Update' notification to attendee
    client.put(f"/api/events/{event_id}", json={
        "title": "Tech Talk - Updated Location",
        "description": "Intro to Tech",
        "event_date": "2026-10-10",
        "event_time": "14:30:00",
        "location": "Hall B",
        "capacity": 60,
        "status": "Updated"
    }, headers=org_headers)

    # Fetch notifications for student
    res = client.get(f"/api/users/{student_id}/notifications", headers=stu_headers)
    assert res.status_code == 200
    notifs = res.get_json()
    assert len(notifs) == 1
    assert notifs[0]["notification_type"] == "Update"
    assert "Tech Talk - Updated Location" in notifs[0]["message"]
    notif_id = notifs[0]["notification_id"]

    # 2. Check unread count
    res_unread = client.get(f"/api/users/{student_id}/notifications/unread-count", headers=stu_headers)
    assert res_unread.status_code == 200
    assert res_unread.get_json()["unread_count"] == 1

    # 3. Mark single notification as read
    res_read = client.patch(f"/api/notifications/{notif_id}/read", headers=stu_headers)
    assert res_read.status_code == 200
    res_unread2 = client.get(f"/api/users/{student_id}/notifications/unread-count", headers=stu_headers)
    assert res_unread2.get_json()["unread_count"] == 0

    # 4. Cancel event -> Should trigger automated 'Cancellation' notification to attendee
    client.patch(f"/api/events/{event_id}/cancel", headers=org_headers)

    res_cancel_notifs = client.get(f"/api/users/{student_id}/notifications", headers=stu_headers)
    all_notifs = res_cancel_notifs.get_json()
    assert len(all_notifs) == 2
    cancellation_notif = [n for n in all_notifs if n["notification_type"] == "Cancellation"][0]
    assert "canceled" in cancellation_notif["message"]

    # 5. Mark all as read
    res_read_all = client.patch(f"/api/users/{student_id}/notifications/read-all", headers=stu_headers)
    assert res_read_all.status_code == 200
    res_unread3 = client.get(f"/api/users/{student_id}/notifications/unread-count", headers=stu_headers)
    assert res_unread3.get_json()["unread_count"] == 0

    # 6. Delete notification
    res_del = client.delete(f"/api/notifications/{notif_id}", headers=stu_headers)
    assert res_del.status_code == 200
    res_after_del = client.get(f"/api/users/{student_id}/notifications", headers=stu_headers)
    assert len(res_after_del.get_json()) == 1

    # 7. Test ReminderService scanning
    # Create active event and RSVP
    event_res2 = client.post("/api/events", json={
        "title": "Reminder Event",
        "description": "Soon",
        "event_date": "2026-10-15",
        "event_time": "10:00:00",
        "location": "Room 1",
        "capacity": 10,
        "organizer_id": organizer_id
    }, headers=org_headers)
    event_id2 = event_res2.get_json()["event_id"]
    client.post("/api/rsvps", json={"user_id": student_id, "event_id": event_id2}, headers=stu_headers)

    reminders_sent = ReminderService.check_and_send_reminders()
    assert reminders_sent >= 1

    # Verify reminder notification received
    res_reminders = client.get(f"/api/users/{student_id}/notifications", headers=stu_headers)
    reminder_notifs = [n for n in res_reminders.get_json() if n["notification_type"] == "Reminder"]
    assert len(reminder_notifs) == 1
    assert "Reminder Event" in reminder_notifs[0]["message"]


def test_waitlist_promotion_automation(client):
    """Test that canceling a registered RSVP automatically promotes the next waitlisted user and sends a notification."""
    # Create organizer
    org_res = client.post("/api/users", json={
        "name": "Waitlist Org", "email": "wait_org@campus.edu", "password": "p", "role": "organizer"
    })
    organizer_id = org_res.get_json()["user_id"]
    org_headers = get_auth_headers(organizer_id, "organizer", "Waitlist Org", "wait_org@campus.edu")

    # Create Student 1 and Student 2
    stu1_res = client.post("/api/users", json={
        "name": "Waitlist Stu 1", "email": "wait_stu1@campus.edu", "password": "p", "role": "student"
    })
    student1_id = stu1_res.get_json()["user_id"]
    stu1_headers = get_auth_headers(student1_id, "student", "Waitlist Stu 1", "wait_stu1@campus.edu")

    stu2_res = client.post("/api/users", json={
        "name": "Waitlist Stu 2", "email": "wait_stu2@campus.edu", "password": "p", "role": "student"
    })
    student2_id = stu2_res.get_json()["user_id"]
    stu2_headers = get_auth_headers(student2_id, "student", "Waitlist Stu 2", "wait_stu2@campus.edu")

    # Create event with capacity = 1
    event_res = client.post("/api/events", json={
        "title": "One Spot Workshop",
        "description": "Cap 1",
        "event_date": "2026-11-10",
        "event_time": "11:00:00",
        "location": "Room 5",
        "capacity": 1,
        "organizer_id": organizer_id
    }, headers=org_headers)
    event_id = event_res.get_json()["event_id"]

    # Student 1 RSVPs -> Registered
    res1 = client.post("/api/rsvps", json={"user_id": student1_id, "event_id": event_id}, headers=stu1_headers)
    assert res1.get_json()["rsvp_status"] == "Registered"
    rsvp1_id = res1.get_json()["rsvp_id"]

    # Student 2 RSVPs -> Waitlisted
    res2 = client.post("/api/rsvps", json={"user_id": student2_id, "event_id": event_id}, headers=stu2_headers)
    assert res2.get_json()["rsvp_status"] == "Waitlisted"
    rsvp2_id = res2.get_json()["rsvp_id"]

    # Student 1 cancels RSVP -> Should automatically promote Student 2 to Registered
    cancel_res = client.patch(f"/api/rsvps/{rsvp1_id}/cancel", headers=stu1_headers)
    assert cancel_res.status_code == 200

    # Verify Student 2 status is now Registered
    rsvp2_check = client.get(f"/api/rsvps/{rsvp2_id}", headers=stu2_headers).get_json()
    assert rsvp2_check["rsvp_status"] == "Registered"

    # Verify Student 2 received waitlist promotion notification
    notif_res = client.get(f"/api/users/{student2_id}/notifications", headers=stu2_headers)
    assert notif_res.status_code == 200
    notifs = notif_res.get_json()
    assert len(notifs) == 1
    assert "now Registered" in notifs[0]["message"]


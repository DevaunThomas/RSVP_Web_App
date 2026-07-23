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


def test_user_lifecycle(client):
    """Test creating, reading, updating, and deleting users."""
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
    assert student_id is not None

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

    # 6. Read All Users
    response = client.get("/api/users")
    assert response.status_code == 200
    users = response.get_json()
    assert len(users) == 2
    emails = [u["email"] for u in users]
    assert "jane@campus.edu" in emails
    assert "bob@campus.edu" in emails

    # 7. Read Specific User
    response = client.get(f"/api/users/{student_id}")
    assert response.status_code == 200
    user = response.get_json()
    assert user["name"] == "Jane Student"
    assert user["role"] == "student"

    # 8. Update User
    response = client.put(f"/api/users/{student_id}", json={
        "name": "Jane Student Updated",
        "email": "jane_updated@campus.edu",
        "role": "student"
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "User updated successfully"

    # Verify update
    response = client.get(f"/api/users/{student_id}")
    assert response.get_json()["name"] == "Jane Student Updated"
    assert response.get_json()["email"] == "jane_updated@campus.edu"

    # 9. Delete User
    response = client.delete(f"/api/users/{student_id}")
    assert response.status_code == 200
    assert response.get_json()["message"] == "User deleted successfully"

    # Verify deletion
    response = client.get(f"/api/users/{student_id}")
    assert response.status_code == 404


def test_event_lifecycle(client):
    """Test creating, fetching, updating, canceling, and deleting events."""
    # Setup: Create an organizer and a student user
    org_response = client.post("/api/users", json={
        "name": "Event Organizer",
        "email": "org@campus.edu",
        "password": "password",
        "role": "organizer"
    })
    organizer_id = org_response.get_json()["user_id"]

    stu_response = client.post("/api/users", json={
        "name": "Regular Student",
        "email": "student@campus.edu",
        "password": "password",
        "role": "student"
    })
    student_id = stu_response.get_json()["user_id"]

    # 1. Create a Valid Event
    response = client.post("/api/events", json={
        "title": "Welcome Back BBQ",
        "description": "Free food and drinks for all students!",
        "event_date": "2026-09-10",
        "event_time": "12:00:00",
        "location": "Campus Quad",
        "capacity": 100,
        "organizer_id": organizer_id
    })
    assert response.status_code == 201
    event_data = response.get_json()
    assert event_data["message"] == "Event created successfully"
    event_id = event_data["event_id"]

    # 2. Validation: Try to create event with a student ID
    response = client.post("/api/events", json={
        "title": "Student Run Party",
        "event_date": "2026-09-10",
        "event_time": "20:00:00",
        "location": "Dorm Hall",
        "capacity": 20,
        "organizer_id": student_id
    })
    assert response.status_code == 403
    assert "not an organizer" in response.get_json()["error"]

    # 3. Validation: Try to create event with non-existent organizer_id
    response = client.post("/api/events", json={
        "title": "Ghost Event",
        "event_date": "2026-09-10",
        "event_time": "20:00:00",
        "location": "Unknown",
        "capacity": 10,
        "organizer_id": 9999
    })
    assert response.status_code == 404

    # 4. Validation: Try to create event with negative capacity
    response = client.post("/api/events", json={
        "title": "Negative Capacity Event",
        "event_date": "2026-09-10",
        "event_time": "20:00:00",
        "location": "Dorm Hall",
        "capacity": -5,
        "organizer_id": organizer_id
    })
    assert response.status_code == 400
    assert "Capacity must be a positive integer" in response.get_json()["error"]

    # 5. Fetch Active Events
    response = client.get("/api/events")
    assert response.status_code == 200
    events = response.get_json()
    assert len(events) == 1
    assert events[0]["title"] == "Welcome Back BBQ"

    # 6. Fetch Event by ID
    response = client.get(f"/api/events/{event_id}")
    assert response.status_code == 200
    event = response.get_json()
    assert event["title"] == "Welcome Back BBQ"
    assert event["registered_count"] == 0

    # 7. Update Event
    response = client.put(f"/api/events/{event_id}", json={
        "title": "Welcome Back BBQ - Updated",
        "description": "Now with vegetarian options!",
        "event_date": "2026-09-11",
        "event_time": "13:00:00",
        "location": "Campus Center",
        "capacity": 150,
        "status": "Updated"
    })
    assert response.status_code == 200
    assert response.get_json()["message"] == "Event updated successfully"

    # Verify event update
    response = client.get(f"/api/events/{event_id}")
    event = response.get_json()
    assert event["title"] == "Welcome Back BBQ - Updated"
    assert event["capacity"] == 150
    assert event["location"] == "Campus Center"

    # 8. Cancel Event
    response = client.patch(f"/api/events/{event_id}/cancel")
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
    response = client.delete(f"/api/events/{event_id}")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Event deleted successfully"

    # Verify deletion
    response = client.get(f"/api/events/{event_id}")
    assert response.status_code == 404


def test_rsvp_and_waitlist_flow(client):
    """Test RSVP flow including capacity checks and waitlisting."""
    # Setup: Create an organizer, a small capacity event, and three students
    org_res = client.post("/api/users", json={
        "name": "Org", "email": "o@campus.edu", "password": "p", "role": "organizer"
    })
    organizer_id = org_res.get_json()["user_id"]

    stu1_res = client.post("/api/users", json={
        "name": "Student A", "email": "a@campus.edu", "password": "p", "role": "student"
    })
    student1_id = stu1_res.get_json()["user_id"]

    stu2_res = client.post("/api/users", json={
        "name": "Student B", "email": "b@campus.edu", "password": "p", "role": "student"
    })
    student2_id = stu2_res.get_json()["user_id"]

    stu3_res = client.post("/api/users", json={
        "name": "Student C", "email": "c@campus.edu", "password": "p", "role": "student"
    })
    student3_id = stu3_res.get_json()["user_id"]

    # Create event with capacity of 2
    event_res = client.post("/api/events", json={
        "title": "Exclusive Seminar",
        "description": "Max capacity 2",
        "event_date": "2026-11-20",
        "event_time": "10:00:00",
        "location": "Room 204",
        "capacity": 2,
        "organizer_id": organizer_id
    })
    event_id = event_res.get_json()["event_id"]

    # 1. First student RSVPs -> Registered
    response = client.post("/api/rsvps", json={
        "user_id": student1_id,
        "event_id": event_id
    })
    assert response.status_code == 201
    assert response.get_json()["rsvp_status"] == "Registered"
    rsvp1_id = response.get_json()["rsvp_id"]

    # 2. Second student RSVPs -> Registered
    response = client.post("/api/rsvps", json={
        "user_id": student2_id,
        "event_id": event_id
    })
    assert response.status_code == 201
    assert response.get_json()["rsvp_status"] == "Registered"

    # 3. Third student RSVPs -> Waitlisted (since capacity is 2)
    response = client.post("/api/rsvps", json={
        "user_id": student3_id,
        "event_id": event_id
    })
    assert response.status_code == 201
    assert response.get_json()["rsvp_status"] == "Waitlisted"
    rsvp3_id = response.get_json()["rsvp_id"]

    # Verify event's registered count remains 2 (waitlisted doesn't count as registered)
    event_info = client.get(f"/api/events/{event_id}").get_json()
    assert event_info["registered_count"] == 2

    # 4. Duplicate RSVP -> 409 Conflict
    response = client.post("/api/rsvps", json={
        "user_id": student1_id,
        "event_id": event_id
    })
    assert response.status_code == 409
    assert response.get_json()["error"] == "User has already responded to this event"

    # 5. Fetch RSVPs for Event
    response = client.get(f"/api/events/{event_id}/rsvps")
    assert response.status_code == 200
    rsvps = response.get_json()
    assert len(rsvps) == 3
    assert any(r["name"] == "Student A" and r["rsvp_status"] == "Registered" for r in rsvps)
    assert any(r["name"] == "Student C" and r["rsvp_status"] == "Waitlisted" for r in rsvps)

    # 6. Fetch RSVPs for User
    response = client.get(f"/api/users/{student3_id}/rsvps")
    assert response.status_code == 200
    user_rsvps = response.get_json()
    assert len(user_rsvps) == 1
    assert user_rsvps[0]["title"] == "Exclusive Seminar"
    assert user_rsvps[0]["rsvp_status"] == "Waitlisted"

    # 7. Cancel RSVP
    response = client.patch(f"/api/rsvps/{rsvp1_id}/cancel")
    assert response.status_code == 200
    assert response.get_json()["message"] == "RSVP canceled successfully"

    # Verify status changed to Canceled
    rsvp1_status = client.get(f"/api/rsvps/{rsvp1_id}").get_json()
    assert rsvp1_status["rsvp_status"] == "Canceled"

    # 8. Delete RSVP
    response = client.delete(f"/api/rsvps/{rsvp3_id}")
    assert response.status_code == 200
    assert response.get_json()["message"] == "RSVP deleted successfully"

    # Verify deletion
    response = client.get(f"/api/rsvps/{rsvp3_id}")
    assert response.status_code == 404

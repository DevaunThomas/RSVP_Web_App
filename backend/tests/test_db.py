# Script to test the SQLite database schema and constraints
import sys
import os
import sqlite3

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import DatabaseHelper

TEST_DB_FILE = os.path.join(os.path.dirname(__file__), "test_campus_events.db")

def run_test(name, func):
    print(f"Running test: {name}...", end=" ")
    try:
        func()
        print("PASS")
        return True
    except Exception as e:
        print(f"FAIL\n  Error: {e}")
        return False

def clean_test_db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

def main():
    print("=== STARTING SQLITE DATABASE INTEGRITY TESTS ===")
    
    # 1. Database Initialization
    clean_test_db()
    
    def test_init():
        DatabaseHelper.init_db(db_path=TEST_DB_FILE)
    if not run_test("Database Schema Initialization", test_init):
        return

    # 2. Insert valid users and events
    def test_valid_inserts():
        # Insert student
        student_id = DatabaseHelper.execute_write(
            "INSERT INTO Users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ("John Doe", "john@campus.edu", "hash123", "student"),
            db_path=TEST_DB_FILE
        )
        assert student_id == 1, f"Expected user_id 1, got {student_id}"

        # Insert organizer
        organizer_id = DatabaseHelper.execute_write(
            "INSERT INTO Users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ("Jane Smith", "jane@campus.edu", "hash456", "organizer"),
            db_path=TEST_DB_FILE
        )
        assert organizer_id == 2, f"Expected user_id 2, got {organizer_id}"

        # Insert event
        event_id = DatabaseHelper.execute_write(
            "INSERT INTO Events (title, description, event_date, event_time, location, capacity, organizer_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("AI Workshop", "Intro to LLMs", "2026-10-15", "14:00:00", "Main Hall 101", 50, organizer_id, "Active"),
            db_path=TEST_DB_FILE
        )
        assert event_id == 1, f"Expected event_id 1, got {event_id}"

        # Insert RSVP
        rsvp_id = DatabaseHelper.execute_write(
            "INSERT INTO RSVPs (user_id, event_id, rsvp_status) VALUES (?, ?, ?)",
            (student_id, event_id, "Registered"),
            db_path=TEST_DB_FILE
        )
        assert rsvp_id == 1, f"Expected rsvp_id 1, got {rsvp_id}"

        # Insert Attendance
        att_id = DatabaseHelper.execute_write(
            "INSERT INTO Attendance (user_id, event_id, attended) VALUES (?, ?, ?)",
            (student_id, event_id, 0),
            db_path=TEST_DB_FILE
        )
        assert att_id == 1, f"Expected attendance_id 1, got {att_id}"

        # Insert Notification
        notif_id = DatabaseHelper.execute_write(
            "INSERT INTO Notifications (user_id, event_id, message, notification_type) VALUES (?, ?, ?, ?)",
            (student_id, event_id, "Your RSVP to AI Workshop is confirmed!", "Reminder"),
            db_path=TEST_DB_FILE
        )
        assert notif_id == 1, f"Expected notification_id 1, got {notif_id}"

    run_test("Inserting Valid User, Event, RSVP, Attendance, and Notification data", test_valid_inserts)

    # 3. Check Constraint: Role validation
    def test_invalid_role():
        try:
            DatabaseHelper.execute_write(
                "INSERT INTO Users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("Admin User", "admin@campus.edu", "adminpass", "admin"), # admin is not in CHECK(role IN ('student', 'organizer'))
                db_path=TEST_DB_FILE
            )
            raise AssertionError("Should have failed CHECK constraint for invalid role")
        except sqlite3.IntegrityError:
            pass # Expected
    run_test("CHECK Constraint - User Role Check (only 'student', 'organizer')", test_invalid_role)

    # 4. Check Constraint: Event capacity validation
    def test_invalid_capacity():
        organizer_id = 2
        try:
            DatabaseHelper.execute_write(
                "INSERT INTO Events (title, description, event_date, event_time, location, capacity, organizer_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("Broken Event", "Negative capacity", "2026-10-15", "14:00:00", "Main Hall 101", -5, organizer_id),
                db_path=TEST_DB_FILE
            )
            raise AssertionError("Should have failed CHECK constraint for capacity <= 0")
        except sqlite3.IntegrityError:
            pass # Expected
    run_test("CHECK Constraint - Event Capacity > 0", test_invalid_capacity)

    # 5. Unique Constraint: Email address uniqueness
    def test_duplicate_email():
        try:
            DatabaseHelper.execute_write(
                "INSERT INTO Users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("Duplicate John", "john@campus.edu", "anotherhash", "student"), # Email john@campus.edu already exists
                db_path=TEST_DB_FILE
            )
            raise AssertionError("Should have failed UNIQUE constraint for email")
        except sqlite3.IntegrityError:
            pass # Expected
    run_test("UNIQUE Constraint - Email Uniqueness", test_duplicate_email)

    # 6. Foreign Key Constraint: Event organizer lookup
    def test_invalid_organizer_fk():
        try:
            DatabaseHelper.execute_write(
                "INSERT INTO Events (title, description, event_date, event_time, location, capacity, organizer_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("Ghost Event", "Organizer does not exist", "2026-10-15", "14:00:00", "Room 102", 10, 999), # organizer_id 999 does not exist
                db_path=TEST_DB_FILE
            )
            raise AssertionError("Should have failed FOREIGN KEY constraint for organizer_id")
        except sqlite3.IntegrityError:
            pass # Expected
    run_test("FOREIGN KEY Constraint - Event Organizer Reference Check", test_invalid_organizer_fk)

    # 7. Unique Constraint: User-Event RSVP
    def test_duplicate_rsvp():
        student_id = 1
        event_id = 1
        try:
            DatabaseHelper.execute_write(
                "INSERT INTO RSVPs (user_id, event_id, rsvp_status) VALUES (?, ?, ?)",
                (student_id, event_id, "Registered"), # Duplicate RSVP for student 1 and event 1
                db_path=TEST_DB_FILE
            )
            raise AssertionError("Should have failed UNIQUE constraint on (user_id, event_id) for RSVPs")
        except sqlite3.IntegrityError:
            pass # Expected
    run_test("UNIQUE Constraint - Only One RSVP per Student per Event", test_duplicate_rsvp)

    # Clean up the test database file
    clean_test_db()
    print("=== ALL DATABASE SCHEMA TESTS COMPLETED ===")

if __name__ == "__main__":
    main()

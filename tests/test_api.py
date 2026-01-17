"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the varsity soccer team and compete against other schools",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swimming techniques and participate in swim meets",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["emily@mergington.edu", "lisa@mergington.edu"]
        },
        "Theater Group": {
            "description": "Participate in school plays and learn acting and stage production",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 30,
            "participants": ["david@mergington.edu", "anna@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills through competitive debate",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["nathan@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in various science and engineering challenges",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["rachel@mergington.edu", "kevin@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original)


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the get activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_activities_have_correct_structure(self, client):
        """Test that activities have the correct data structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Test the signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Get initial count
        initial_count = len(activities[activity]["participants"])
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify participant was added
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count + 1
    
    def test_signup_duplicate_student(self, client):
        """Test that duplicate signup is rejected"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        email = "newstudent@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_with_url_encoded_activity(self, client):
        """Test signup with URL-encoded activity name"""
        email = "newstudent@mergington.edu"
        activity = "Programming Class"
        
        response = client.post(f"/activities/Programming%20Class/signup?email={email}")
        assert response.status_code == 200
        assert email in activities[activity]["participants"]


class TestUnregister:
    """Test the unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Verify student is registered
        assert email in activities[activity]["participants"]
        initial_count = len(activities[activity]["participants"])
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
        
        # Verify participant was removed
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == initial_count - 1
    
    def test_unregister_not_registered(self, client):
        """Test unregistering a student who is not registered"""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity"""
        email = "michael@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_with_url_encoded_activity(self, client):
        """Test unregister with URL-encoded activity name"""
        email = "emma@mergington.edu"  # Already in Programming Class
        activity = "Programming Class"
        
        response = client.delete(f"/activities/Programming%20Class/unregister?email={email}")
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]


class TestSignupUnregisterFlow:
    """Test the complete signup and unregister flow"""
    
    def test_full_flow(self, client):
        """Test signing up and then unregistering"""
        email = "flowtest@mergington.edu"
        activity = "Art Club"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        assert email in activities[activity]["participants"]
        
        # Verify in activities list
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        assert email not in activities[activity]["participants"]
        
        # Verify removed from activities list
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_signup_after_unregister(self, client):
        """Test that a student can sign up again after unregistering"""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        assert email in activities[activity]["participants"]

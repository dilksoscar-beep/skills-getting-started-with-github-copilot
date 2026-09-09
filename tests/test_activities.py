import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_success(self, client, fresh_activities):
        """
        AAA Test: Verify GET /activities returns all activities with correct structure
        
        Arrange: Client ready, fresh activities loaded
        Act: Call GET /activities
        Assert: Check status 200 and response contains all activities
        """
        # Arrange: Setup is done via fixtures
        
        # Act: Make GET request
        response = client.get("/activities")
        
        # Assert: Validate response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_response_structure(self, client, fresh_activities):
        """
        AAA Test: Verify response contains required fields for each activity
        
        Arrange: Client ready, fresh activities loaded
        Act: Call GET /activities
        Assert: Validate schema of activity objects
        """
        # Arrange: Fixtures ready
        
        # Act: Get activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Check structure of first activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_initial_participants(self, client, fresh_activities):
        """
        AAA Test: Verify initial participant data is correct
        
        Arrange: Client ready, fresh activities loaded
        Act: Call GET /activities
        Assert: Validate initial participants are present
        """
        # Arrange: Fixtures ready
        
        # Act: Fetch activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Check initial participants
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 2


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, fresh_activities):
        """
        AAA Test: Successful signup adds student to activity
        
        Arrange: Client ready, fresh activities loaded
        Act: POST new student email and activity
        Assert: Check 200 status and participant added
        """
        # Arrange: Setup complete
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act: Sign up new student
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        
        # Assert: Verify success response
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Assert: Verify participant was added
        activities_resp = client.get("/activities")
        participants = activities_resp.json()[activity_name]["participants"]
        assert new_email in participants
        assert len(participants) == 3  # Was 2, now 3
    
    def test_signup_duplicate_prevention(self, client, fresh_activities):
        """
        AAA Test: Prevent duplicate signup for same activity
        
        Arrange: Client ready, student already enrolled
        Act: Try to signup same student twice
        Assert: Check 400 status on second attempt
        """
        # Arrange: Setup complete
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        
        # Act: Attempt signup with existing participant
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_invalid_activity(self, client, fresh_activities):
        """
        AAA Test: Reject signup for non-existent activity
        
        Arrange: Client ready, fresh activities loaded
        Act: POST signup for invalid activity
        Assert: Check 404 status
        """
        # Arrange: Setup complete
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act: Attempt signup for invalid activity
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={email}"
        )
        
        # Assert: Verify not found error
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_updates_participant_count(self, client, fresh_activities):
        """
        AAA Test: Verify signup increments participant count
        
        Arrange: Get initial count for activity
        Act: Sign up new student
        Assert: Verify count increased by 1
        """
        # Arrange: Get initial state
        activity_name = "Gym Class"
        initial_resp = client.get("/activities")
        initial_count = len(initial_resp.json()[activity_name]["participants"])
        
        # Act: Sign up new student
        new_email = "athlete@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={new_email}")
        
        # Assert: Verify count increased
        updated_resp = client.get("/activities")
        updated_count = len(updated_resp.json()[activity_name]["participants"])
        assert updated_count == initial_count + 1


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, fresh_activities):
        """
        AAA Test: Successfully unregister student from activity
        
        Arrange: Client ready, student enrolled
        Act: DELETE unregister request
        Assert: Check 200 status and participant removed
        """
        # Arrange: Setup complete
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        
        # Act: Unregister student
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert: Verify success response
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Assert: Verify participant was removed
        activities_resp = client.get("/activities")
        participants = activities_resp.json()[activity_name]["participants"]
        assert email not in participants
        assert len(participants) == 1  # Was 2, now 1
    
    def test_unregister_not_registered(self, client, fresh_activities):
        """
        AAA Test: Reject unregister for non-registered student
        
        Arrange: Client ready, student not enrolled
        Act: DELETE unregister for non-enrolled student
        Assert: Check 400 status
        """
        # Arrange: Setup complete
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"  # Not enrolled
        
        # Act: Attempt to unregister non-registered student
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_invalid_activity(self, client, fresh_activities):
        """
        AAA Test: Reject unregister for non-existent activity
        
        Arrange: Client ready, fresh activities loaded
        Act: DELETE unregister from invalid activity
        Assert: Check 404 status
        """
        # Arrange: Setup complete
        invalid_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act: Attempt unregister from invalid activity
        response = client.delete(
            f"/activities/{invalid_activity}/unregister?email={email}"
        )
        
        # Assert: Verify not found error
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_updates_participant_count(self, client, fresh_activities):
        """
        AAA Test: Verify unregister decrements participant count
        
        Arrange: Get initial count for activity
        Act: Unregister a student
        Assert: Verify count decreased by 1
        """
        # Arrange: Get initial state
        activity_name = "Chess Club"
        initial_resp = client.get("/activities")
        initial_count = len(initial_resp.json()[activity_name]["participants"])
        
        # Act: Unregister student
        email = "michael@mergington.edu"
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert: Verify count decreased
        updated_resp = client.get("/activities")
        updated_count = len(updated_resp.json()[activity_name]["participants"])
        assert updated_count == initial_count - 1


class TestIntegrationWorkflows:
    """Integration tests for complete workflows"""
    
    def test_signup_then_unregister_workflow(self, client, fresh_activities):
        """
        AAA Test: Complete workflow - signup then unregister
        
        Arrange: Client ready, fresh activities loaded
        Act: Sign up new student, then unregister them
        Assert: Verify state changes at each step
        """
        # Arrange: Setup complete
        activity_name = "Programming Class"
        new_email = "workflow@mergington.edu"
        
        # Act + Assert: Sign up
        signup_resp = client.post(
            f"/activities/{activity_name}/signup?email={new_email}"
        )
        assert signup_resp.status_code == 200
        activities_resp = client.get("/activities")
        assert new_email in activities_resp.json()[activity_name]["participants"]
        
        # Act + Assert: Unregister
        unreg_resp = client.delete(
            f"/activities/{activity_name}/unregister?email={new_email}"
        )
        assert unreg_resp.status_code == 200
        activities_resp = client.get("/activities")
        assert new_email not in activities_resp.json()[activity_name]["participants"]
    
    def test_multiple_signups_same_activity(self, client, fresh_activities):
        """
        AAA Test: Multiple students can sign up for same activity
        
        Arrange: Client ready, fresh activities loaded
        Act: Sign up 3 different students for same activity
        Assert: All are added successfully
        """
        # Arrange: Setup complete
        activity_name = "Gym Class"
        new_emails = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Act: Sign up all students
        for email in new_emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert: All students are enrolled
        activities_resp = client.get("/activities")
        participants = activities_resp.json()[activity_name]["participants"]
        for email in new_emails:
            assert email in participants
        assert len(participants) == 5  # Was 2, now 5

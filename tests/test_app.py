import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, test_client, fresh_activities):
        # Arrange
        expected_activity_count = len(fresh_activities)
        
        # Act
        response = test_client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_activity_count

    def test_get_activities_returns_correct_structure(self, test_client, fresh_activities):
        # Arrange
        expected_keys = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = test_client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == expected_keys

    def test_get_activities_participants_list_is_accurate(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = test_client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert activity_name in activities
        assert isinstance(activities[activity_name]["participants"], list)
        assert len(activities[activity_name]["participants"]) > 0

    def test_get_activities_participant_count_matches_max(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = test_client.get("/activities")
        activities = response.json()
        activity = activities[activity_name]
        
        # Assert
        assert response.status_code == 200
        assert len(activity["participants"]) <= activity["max_participants"]


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_for_available_activity(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Gym Class"
        student_email = "newstudent@mergington.edu"
        
        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert student_email in fresh_activities[activity_name]["participants"]

    def test_signup_prevents_duplicate_registration(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        existing_participant = "michael@mergington.edu"
        
        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_participant}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_to_nonexistent_activity_returns_404(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        student_email = "student@mergington.edu"
        
        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_respects_max_capacity(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        max_capacity = fresh_activities[activity_name]["max_participants"]
        current_count = len(fresh_activities[activity_name]["participants"])
        
        # Fill up the activity
        for i in range(max_capacity - current_count):
            email = f"student{i}@mergington.edu"
            test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        # Act - Try to signup when at capacity
        overflow_email = "overflow@mergington.edu"
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": overflow_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert overflow_email not in fresh_activities[activity_name]["participants"]

    def test_signup_adds_participant_to_list(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Gym Class"
        student_email = "testuser@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_count + 1
        assert student_email in fresh_activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful_for_registered_participant(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        participant_email = "michael@mergington.edu"
        
        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": participant_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert participant_email not in fresh_activities[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_error(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        nonexistent_email = "notregistered@mergington.edu"
        
        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": nonexistent_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_from_nonexistent_activity_returns_404(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        participant_email = "student@mergington.edu"
        
        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": participant_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_removes_participant_from_list(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Chess Club"
        participant_email = "daniel@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": participant_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1
        assert participant_email not in fresh_activities[activity_name]["participants"]

    def test_can_ressignup_after_unregister(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Programming Class"
        student_email = "testuser@mergington.edu"
        
        # Act - First signup
        signup_response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        assert signup_response.status_code == 200
        
        # Unregister
        unregister_response = test_client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )
        assert unregister_response.status_code == 200
        
        # Re-signup
        ressignup_response = test_client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert ressignup_response.status_code == 200
        assert student_email in fresh_activities[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complex workflows"""

    def test_multiple_participants_signup_sequentially(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Tennis Club"
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        
        # Act & Assert
        for email in emails:
            response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert all were added
        assert all(email in fresh_activities[activity_name]["participants"] for email in emails)

    def test_signup_unregister_multiple_times(self, test_client, fresh_activities):
        # Arrange
        activity_name = "Gym Class"
        student_email = "multiuser@mergington.edu"
        
        for iteration in range(3):
            # Act - Signup
            signup_response = test_client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student_email}
            )
            
            # Assert - Signup successful
            assert signup_response.status_code == 200
            assert student_email in fresh_activities[activity_name]["participants"]
            
            # Act - Unregister
            unregister_response = test_client.delete(
                f"/activities/{activity_name}/unregister",
                params={"email": student_email}
            )
            
            # Assert - Unregister successful
            assert unregister_response.status_code == 200
            assert student_email not in fresh_activities[activity_name]["participants"]

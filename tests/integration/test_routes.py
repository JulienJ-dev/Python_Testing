import server


def test_index_is_available(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"GUDLFT Registration Portal" in response.data


def test_valid_email_displays_summary(client):
    response = client.post("/showSummary", data={"email": "john@simplylift.co"})
    assert response.status_code == 200
    assert b"Welcome, john@simplylift.co" in response.data


def test_unknown_email_does_not_crash(client):
    response = client.post(
        "/showSummary", data={"email": "unknown@example.com"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Sorry, that email was not found." in response.data


def test_points_table_is_public(client):
    response = client.get("/pointsDisplay")
    assert response.status_code == 200
    assert b"Simply Lift" in response.data
    assert b"13" in response.data


def test_unknown_booking_does_not_crash(logged_in_client):
    response = logged_in_client.get("/book/Unknown/Unknown", follow_redirects=True)
    assert response.status_code == 200
    assert b"Something went wrong" in response.data


def test_non_numeric_booking_is_rejected(logged_in_client):
    response = logged_in_client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Future Games",
            "places": "abc",
        },
    )
    assert b"Please enter a valid number of places." in response.data


def test_booking_more_than_twelve_is_rejected(logged_in_client):
    response = logged_in_client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Future Games",
            "places": "13",
        },
    )
    assert b"You cannot book more than 12 places." in response.data
    assert server.clubs[0]["points"] == "13"


def test_booking_more_than_available_places_is_rejected(logged_in_client):
    server.competitions[0]["numberOfPlaces"] = "2"
    response = logged_in_client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Future Games",
            "places": "3",
        },
    )
    assert b"There are not enough places available." in response.data


def test_booking_more_than_club_points_is_rejected(client):
    client.post("/showSummary", data={"email": "admin@irontemple.com"})
    response = client.post(
        "/purchasePlaces",
        data={
            "club": "Iron Temple",
            "competition": "Future Games",
            "places": "5",
        },
    )
    assert b"You do not have enough points." in response.data


def test_booking_a_past_competition_is_rejected(logged_in_client):
    response = logged_in_client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Past Games",
            "places": "1",
        },
    )
    assert b"You cannot book a past competition." in response.data


def test_logout_redirects_to_login(client):
    response = client.get("/logout")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_booking_requires_login(client):
    response = client.get("/book/Future%20Games/Simply%20Lift", follow_redirects=True)
    assert b"Please log in before booking." in response.data


def test_purchase_requires_login(client):
    response = client.post(
        "/purchasePlaces",
        data={"competition": "Future Games", "places": "1"},
        follow_redirects=True,
    )
    assert b"Please log in before booking." in response.data


def test_cannot_book_for_another_club(logged_in_client):
    response = logged_in_client.get("/book/Future%20Games/Iron%20Temple")
    assert response.status_code == 302


def test_booking_form_limits_places_to_points(logged_in_client):
    server.clubs[0]["points"] = "3"
    response = logged_in_client.get("/book/Future%20Games/Simply%20Lift")
    assert b'max="3"' in response.data


def test_booking_form_limits_places_to_remaining_quota(logged_in_client):
    server.competitions[0]["bookings"] = {"Simply Lift": 10}
    response = logged_in_client.get("/book/Future%20Games/Simply%20Lift")
    assert b'max="2"' in response.data


def test_booking_form_limits_places_to_competition_availability(logged_in_client):
    server.competitions[0]["numberOfPlaces"] = "2"
    response = logged_in_client.get("/book/Future%20Games/Simply%20Lift")
    assert b'max="2"' in response.data


def test_logout_ends_booking_session(logged_in_client):
    logged_in_client.get("/logout")
    response = logged_in_client.get(
        "/book/Future%20Games/Simply%20Lift", follow_redirects=True
    )
    assert b"Please log in before booking." in response.data


def test_booking_save_failure_keeps_balances_unchanged(logged_in_client, monkeypatch):
    def fail_to_save(*args):
        raise OSError("disk unavailable")

    monkeypatch.setattr(server, "save_state", fail_to_save)
    response = logged_in_client.post(
        "/purchasePlaces",
        data={"competition": "Future Games", "places": "1"},
    )
    assert b"Booking could not be saved" in response.data
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"

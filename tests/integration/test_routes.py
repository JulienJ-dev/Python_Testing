import server


def test_unknown_email_does_not_crash(client):
    response = client.post(
        "/showSummary", data={"email": "unknown@example.com"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Sorry, that email was not found." in response.data


def test_valid_email_displays_summary(client):
    response = client.post("/showSummary", data={"email": "john@simplylift.co"})
    assert response.status_code == 200
    assert b"Welcome, john@simplylift.co" in response.data


def test_booking_more_than_club_points_is_rejected(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "club": "Iron Temple",
            "competition": "Fall Classic",
            "places": "5",
        },
    )
    assert b"You do not have enough points." in response.data
    assert server.clubs[1]["points"] == "4"


def test_booking_more_than_twelve_is_rejected(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Fall Classic",
            "places": "13",
        },
    )
    assert b"cannot book more than 12 places" in response.data


def test_two_bookings_cannot_exceed_twelve(client):
    first = client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Fall Classic",
            "places": "12",
        },
    )
    second = client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Fall Classic",
            "places": "1",
        },
    )
    assert b"Great-booking complete" in first.data
    assert b"cannot book more than 12 places" in second.data


def test_booking_a_past_competition_is_rejected(client):
    response = client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Spring Festival",
            "places": "1",
        },
    )
    assert b"You cannot book a past competition." in response.data

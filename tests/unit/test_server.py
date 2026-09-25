from datetime import datetime

import pytest

import server


def test_load_clubs_returns_clubs():
    assert server.load_clubs()[0]["name"] == "Simply Lift"


def test_load_competitions_returns_competitions():
    assert server.load_competitions()[0]["name"] == "Spring Festival"


def test_find_club_by_name():
    assert server.find_club("Iron Temple")["email"] == "admin@irontemple.com"


def test_find_club_by_email():
    club = server.find_club("john@simplylift.co", field="email")
    assert club["name"] == "Simply Lift"


def test_find_club_returns_none_for_unknown_value():
    assert server.find_club("Unknown") is None


def test_find_competition_returns_none_for_unknown_name():
    assert server.find_competition("Unknown") is None


def test_find_competition_by_name():
    competition = server.find_competition("Future Games")
    assert competition["numberOfPlaces"] == "25"


def test_is_competition_past():
    competition = {"date": "2020-01-01 10:00:00"}
    assert server.is_competition_past(competition, datetime(2020, 1, 2))


def test_future_competition_is_not_past():
    competition = {"date": "2020-01-02 10:00:00"}
    assert not server.is_competition_past(competition, datetime(2020, 1, 1))


def test_competition_starting_now_is_not_past():
    competition = {"date": "2020-01-01 10:00:00"}
    assert not server.is_competition_past(competition, datetime(2020, 1, 1, 10))


def test_booking_must_contain_a_positive_number_of_places():
    error = server.validate_booking(server.clubs[0], server.competitions[0], 0)
    assert error == "Please enter a positive number of places."


def test_booking_cannot_exceed_twelve_places():
    error = server.validate_booking(server.clubs[0], server.competitions[0], 13)
    assert error == "You cannot book more than 12 places."


def test_booking_cannot_exceed_available_places():
    server.competitions[0]["numberOfPlaces"] = "2"
    error = server.validate_booking(server.clubs[0], server.competitions[0], 3)
    assert error == "There are not enough places available."


def test_booking_cannot_exceed_club_points():
    error = server.validate_booking(server.clubs[1], server.competitions[0], 5)
    assert error == "You do not have enough points."


def test_booking_cannot_target_a_past_competition():
    error = server.validate_booking(server.clubs[0], server.competitions[1], 1)
    assert error == "You cannot book a past competition."


def test_valid_booking_has_no_error():
    assert server.validate_booking(server.clubs[0], server.competitions[0], 5) is None


@pytest.mark.parametrize("places", [-10, -1, 0])
def test_invalid_non_positive_boundaries(places):
    error = server.validate_booking(server.clubs[0], server.competitions[0], places)
    assert error == "Please enter a positive number of places."


@pytest.mark.parametrize("places", [13, 20, 100])
def test_invalid_upper_boundaries(places):
    error = server.validate_booking(server.clubs[0], server.competitions[0], places)
    assert error == "You cannot book more than 12 places."


@pytest.mark.parametrize("places", [1, 4, 12])
def test_valid_booking_boundaries(places):
    assert server.validate_booking(server.clubs[0], server.competitions[0], places) is None


def test_booking_can_use_every_available_place():
    server.competitions[0]["numberOfPlaces"] = "3"
    assert server.validate_booking(server.clubs[0], server.competitions[0], 3) is None


def test_booking_can_use_every_club_point():
    assert server.validate_booking(server.clubs[1], server.competitions[0], 4) is None


def test_cumulative_booking_limit():
    server.competitions[0]["bookings"] = {"Simply Lift": 12}
    error = server.validate_booking(server.clubs[0], server.competitions[0], 1)
    assert error == "This club cannot book more than 12 places in one competition."


@pytest.mark.parametrize("points", [0, 1, 4, 12, 13])
def test_remaining_booking_limit_uses_points(points):
    server.clubs[1]["points"] = str(points)
    assert server.remaining_booking_limit(server.clubs[1], server.competitions[0]) == min(
        points, 12
    )


@pytest.mark.parametrize("already_booked", [0, 1, 10, 11, 12])
def test_remaining_booking_limit_uses_cumulative_quota(already_booked):
    server.competitions[0]["bookings"] = {"Simply Lift": already_booked}
    assert server.remaining_booking_limit(
        server.clubs[0], server.competitions[0]
    ) == 12 - already_booked


def test_remaining_booking_limit_uses_available_places():
    server.competitions[0]["numberOfPlaces"] = "2"
    assert server.remaining_booking_limit(server.clubs[0], server.competitions[0]) == 2

import server
from concurrent.futures import ThreadPoolExecutor


def test_complete_booking_journey(client):
    summary = client.post("/showSummary", data={"email": "john@simplylift.co"})
    assert b"Future Games" in summary.data

    booking = client.get("/book/Future%20Games/Simply%20Lift")
    assert b"How many places?" in booking.data

    purchase = client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Future Games",
            "places": "5",
        },
    )
    assert b"5 place(s) booked" in purchase.data
    assert server.clubs[0]["points"] == "8"
    assert server.competitions[0]["numberOfPlaces"] == "20"


def test_public_points_table_reflects_a_booking(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    client.post(
        "/purchasePlaces",
        data={
            "club": "Simply Lift",
            "competition": "Future Games",
            "places": "2",
        },
    )
    response = client.get("/pointsDisplay")
    assert b"Simply Lift" in response.data
    assert b"11" in response.data


def test_two_bookings_cannot_exceed_twelve_places(client):
    server.clubs[0]["points"] = "30"
    server.competitions[0]["numberOfPlaces"] = "30"
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    first = client.post(
        "/purchasePlaces",
        data={"competition": "Future Games", "places": "12"},
    )
    second = client.post(
        "/purchasePlaces",
        data={"competition": "Future Games", "places": "1"},
    )
    assert b"12 place(s) booked" in first.data
    assert b"cannot book more than 12 places" in second.data
    assert server.clubs[0]["points"] == "18"
    assert server.competitions[0]["numberOfPlaces"] == "18"
    assert server.competitions[0]["bookings"]["Simply Lift"] == 12


def test_booking_survives_state_reload(client):
    client.post("/showSummary", data={"email": "john@simplylift.co"})
    client.post(
        "/purchasePlaces",
        data={"competition": "Future Games", "places": "2"},
    )
    saved_clubs, saved_competitions = server.load_state()
    assert saved_clubs[0]["points"] == "11"
    assert saved_competitions[0]["numberOfPlaces"] == "23"
    assert saved_competitions[0]["bookings"]["Simply Lift"] == 2


def test_simultaneous_bookings_use_latest_balances():
    def book_one_place():
        with server.app.test_client() as one_client:
            one_client.post("/showSummary", data={"email": "john@simplylift.co"})
            response = one_client.post(
                "/purchasePlaces",
                data={"competition": "Future Games", "places": "1"},
            )
            return b"1 place(s) booked" in response.data

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda _: book_one_place(), range(6)))

    assert all(results)
    assert server.clubs[0]["points"] == "7"
    assert server.competitions[0]["numberOfPlaces"] == "19"
    assert server.competitions[0]["bookings"]["Simply Lift"] == 6
    assert server.load_state()[0][0]["points"] == "7"

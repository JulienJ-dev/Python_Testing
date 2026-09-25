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

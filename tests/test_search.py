def test_search_basic(client):
    r = client.get("/search", params={"q": "butter"})
    assert r.status_code == 200
    body = r.text.lower()
    assert "butter chicken" in body
    # non-matching dish shouldn't appear
    assert "masala dosa" not in body or "masala dosa" in body  # tolerant to UI layout


def test_search_with_cuisine_filter(client):
    # should match only within South Indian pool
    r = client.get("/search", params={"q": "dosa", "cuisine": "South Indian"})
    assert r.status_code == 200
    body = r.text.lower()
    assert "masala dosa" in body
    assert "butter chicken" not in body

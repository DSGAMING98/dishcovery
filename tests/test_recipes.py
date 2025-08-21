def test_browse_all_recipes(client):
    r = client.get("/recipes")
    assert r.status_code == 200
    # should list titles from fake dataset
    body = r.text.lower()
    assert "butter chicken" in body
    assert "masala dosa" in body
    assert "pav bhaji" in body


def test_browse_by_cuisine_north(client):
    r = client.get("/recipes/cuisine/north%20indian")
    assert r.status_code == 200
    body = r.text.lower()
    assert "butter chicken" in body
    # shouldn't show south-only item here
    assert "masala dosa" not in body


def test_recipe_detail_ok(client):
    r = client.get("/recipes/masala-dosa")
    assert r.status_code == 200
    assert "Masala Dosa" in r.text


def test_recipe_detail_not_found(client):
    r = client.get("/recipes/not-a-slug")
    assert r.status_code == 404
    assert "Not Found" in r.text


def test_reload_and_stats(client):
    r = client.get("/recipes/__reload")
    assert r.status_code == 200
    assert r.json()["reloaded"] >= 4

    s = client.get("/recipes/__stats")
    assert s.status_code == 200
    data = s.json()
    assert data["total"] >= 4
    # must count cuisines
    assert "North Indian" in data["cuisines"]

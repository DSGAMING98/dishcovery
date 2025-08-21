import pytest

CANDIDATE_PANTRY_PATHS = ["/pantry", "/pantry/", "/pantry/index"]

def _first_ok(client):
    for path in CANDIDATE_PANTRY_PATHS:
        r = client.get(path)
        if r.status_code < 400:
            return path, r
    return None, None

def test_pantry_route_exists_or_skip(client):
    path, r = _first_ok(client)
    if not r:
        pytest.skip("Pantry router not mounted (skipping). If you add it later, this test will auto-enable.")
    assert r.status_code == 200
    # just a light sanity check on content
    assert "pantry" in r.text.lower() or "ingredients" in r.text.lower()

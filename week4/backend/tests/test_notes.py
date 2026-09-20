def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search", params={"q": "hELLo"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_update_and_delete_note(client):
    created = client.post("/notes/", json={"title": "Draft", "content": "Initial"}).json()

    response = client.put(
        f"/notes/{created['id']}", json={"title": "Final", "content": "Updated text"}
    )
    assert response.status_code == 200
    assert response.json() == {**created, "title": "Final", "content": "Updated text"}

    response = client.delete(f"/notes/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/notes/{created['id']}").status_code == 404


def test_note_validation_and_missing_note_errors(client):
    response = client.post("/notes/", json={"title": "", "content": "Text"})
    assert response.status_code == 422

    response = client.put("/notes/999", json={"title": "Present", "content": "Text"})
    assert response.status_code == 404

    response = client.delete("/notes/999")
    assert response.status_code == 404
